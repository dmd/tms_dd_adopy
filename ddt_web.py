#!/usr/bin/env python3
"""Web-based interface for the DDT ADO experiment, using Flask."""
import random
import json
import uuid
import os
import logging
from pathlib import Path
from datetime import datetime
from threading import Lock
import tempfile

import yaml
import boto3
import pandas as pd
from flask import Flask, render_template, request, jsonify, session
from flask import make_response
from serverless_wsgi import handle_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ddt_core import DdtCore

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "ddt-experiment-secret-key-change-in-production"
)

# S3 configuration
S3_BUCKET = "3e.org"
s3_client = boto3.client("s3")

# S3-based storage for active experiments
def save_experiment_to_s3(session_id, exp_data):
    """Save experiment data to S3"""
    try:
        # Convert experiment object to serializable format
        serializable_data = {
            "config": exp_data["config"],
            "last_design": exp_data["last_design"],
            "created_at": exp_data["created_at"].isoformat(),
            "exp_state": {
                "subject": exp_data["exp"].subject,
                "session": exp_data["exp"].session,
                "path_output": str(exp_data["exp"].path_output),
                "df": exp_data["exp"].df.to_dict(),
                "block": exp_data["exp"].block,
                "block_type": exp_data["exp"].block_type,
            },
        }
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=f"ddt-sessions/{session_id}.json",
            Body=json.dumps(serializable_data),
            ContentType="application/json",
        )
    except Exception as e:
        logger.error(f"Error saving experiment to S3: {e}")
        raise


def load_experiment_from_s3(session_id):
    """Load experiment data from S3"""
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET, Key=f"ddt-sessions/{session_id}.json"
        )
        data = json.loads(response["Body"].read())

        # Recreate experiment object
        exp_state = data["exp_state"]
        exp = DdtCore(
            exp_state["subject"], exp_state["session"], Path(exp_state["path_output"])
        )
        exp.df = pd.DataFrame.from_dict(exp_state["df"])
        exp.block = exp_state["block"]
        exp.block_type = exp_state["block_type"]
        # Restore the ADO engine state from saved trials
        exp.restore_engine_state()

        return {
            "exp": exp,
            "config": data["config"],
            "last_design": data["last_design"],
            "created_at": datetime.fromisoformat(data["created_at"]),
        }
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        logger.error(f"Error loading experiment from S3: {e}")
        return None


@app.route("/", methods=["GET"])
def index():
    logger.info("Index page accessed")
    return render_template("index.html")

@app.route("/debug", methods=["GET"])
def debug():
    """Debug endpoint to test S3 operations"""
    try:
        # List recent sessions
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="ddt-sessions/")
        sessions = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug/<session_id>", methods=["GET"])
def debug_session(session_id):
    """Debug endpoint to test loading a specific session"""
    try:
        # Test each step of load_experiment_from_s3
        s3_key = f"ddt-sessions/{session_id}.json"
        
        # Step 1: Get object from S3
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
            raw_data = response['Body'].read()
        except s3_client.exceptions.NoSuchKey:
            return jsonify({"status": "s3_object_not_found", "key": s3_key})
        except Exception as e:
            return jsonify({"status": "s3_error", "error": str(e)})
        
        # Step 2: Parse JSON
        try:
            data = json.loads(raw_data)
        except Exception as e:
            return jsonify({"status": "json_parse_error", "error": str(e)})
        
        # Step 3: Extract exp_state
        try:
            exp_state = data["exp_state"]
        except Exception as e:
            return jsonify({"status": "exp_state_error", "error": str(e)})
        
        # Step 4: Create DdtCore object
        try:
            from pathlib import Path
            exp = DdtCore(exp_state["subject"], exp_state["session"], Path(exp_state["path_output"]))
        except Exception as e:
            return jsonify({"status": "ddtcore_creation_error", "error": str(e)})
        
        # Step 5: Restore DataFrame
        try:
            exp.df = pd.DataFrame.from_dict(exp_state["df"])
            exp.block = exp_state["block"]
            exp.block_type = exp_state["block_type"]
        except Exception as e:
            return jsonify({"status": "dataframe_error", "error": str(e)})
        
        # Step 6: Restore engine state
        try:
            exp.restore_engine_state()
        except Exception as e:
            return jsonify({"status": "restore_engine_error", "error": str(e)})
        
        return jsonify({
            "status": "success",
            "exp_state_keys": list(exp_state.keys()),
            "df_shape": exp.df.shape if hasattr(exp, 'df') else "no df"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/start", methods=["POST"])
def start():
    subject = int(request.form.get("subject_id"))
    session_num = int(request.form.get("session"))
    num_train = int(request.form.get("num_train_trials"))
    num_main = int(request.form.get("num_main_trials"))
    show_tutorial = bool(request.form.get("show_tutorial"))

    # Generate unique session ID for this experiment
    session_id = str(uuid.uuid4())

    time_now_iso = datetime.now().isoformat().replace(":", "-")[:-7]
    # Use temporary file for Lambda environment
    filename = f"DDT{subject:03d}_ses{session_num}_{time_now_iso}.csv"
    path_output = Path(tempfile.gettempdir()) / filename

    # Create experiment instance for this session
    exp = DdtCore(subject, session_num, path_output)

    instr_path = Path(__file__).parent / "instructions.yml"
    with open(instr_path, "r", encoding="utf-8") as f:
        instructions = yaml.safe_load(f)
    instructions["main_before"] = instructions["main_before"].format(num_main)

    config = {
        "subject_id": subject,
        "session": session_num,
        "num_train_trials": num_train,
        "num_main_trials": num_main,
        "show_tutorial": show_tutorial,
        "instructions": instructions,
        "session_id": session_id,
    }

    # Store experiment data in S3
    exp_data = {
        "exp": exp,
        "config": config,
        "last_design": None,
        "created_at": datetime.now(),
    }
    save_experiment_to_s3(session_id, exp_data)

    return render_template("experiment.html", config_json=json.dumps(config))


@app.route("/next_design", methods=["GET"])
def next_design():
    session_id = request.args.get("session_id")
    logger.info(f"next_design called with session_id: {session_id}")
    if not session_id:
        logger.error("No session_id provided")
        return jsonify({"error": "Invalid session"}), 400

    # Load experiment data from S3
    try:
        exp_data = load_experiment_from_s3(session_id)
        if not exp_data:
            logger.error(f"Session {session_id} not found in S3")
            return jsonify({"error": "Invalid session"}), 400
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {e}")
        return jsonify({"error": "Invalid session"}), 400

    exp = exp_data["exp"]
    mode = request.args.get("mode", "optimal")
    engine_mode = "random" if mode == "train" else mode
    design = exp.get_design(engine_mode)
    exp_data["last_design"] = design

    # Save updated state back to S3
    save_experiment_to_s3(session_id, exp_data)

    direction = random.randint(0, 1)
    return jsonify({"design": design, "direction": direction})


@app.route("/response", methods=["POST"])
def response():
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Invalid session"}), 400

    # Load experiment data from S3
    try:
        exp_data = load_experiment_from_s3(session_id)
        if not exp_data:
            logger.error(f"Session {session_id} not found in S3")
            return jsonify({"error": "Invalid session"}), 400
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {e}")
        return jsonify({"error": "Invalid session"}), 400

    exp = exp_data["exp"]
    config = exp_data["config"]
    last_design = exp_data["last_design"]

    mode = data.get("mode")
    if mode == "train":
        exp_data["last_design"] = None
        save_experiment_to_s3(session_id, exp_data)
        return jsonify({"success": True})

    resp_left = int(data.get("resp_left"))
    direction = int(data.get("direction"))
    rt = float(data.get("rt"))
    resp_ss = resp_left if direction == 1 else 1 - resp_left

    exp.update_and_record(last_design, resp_ss, rt)
    exp_data["last_design"] = None

    finished = len(exp.df) >= config["num_main_trials"]
    if finished:
        # Save to S3 instead of local file
        exp.save_record_to_s3(s3_client, S3_BUCKET)
        # Clean up completed experiment from S3
        try:
            s3_client.delete_object(
                Bucket=S3_BUCKET, Key=f"ddt-sessions/{session_id}.json"
            )
        except Exception as e:
            logger.error(f"Error cleaning up session: {e}")
    else:
        # Save updated state back to S3
        save_experiment_to_s3(session_id, exp_data)

    return jsonify({"finished": finished})


# Note: Session cleanup now handled by S3 object lifecycle policies
# Old sessions will be automatically cleaned up by AWS


def lambda_handler(event, context):
    """AWS Lambda handler function."""
    return handle_request(app, event, context)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
