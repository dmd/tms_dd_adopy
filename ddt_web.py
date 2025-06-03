#!/usr/bin/env python3
"""Web-based interface for the DDT ADO experiment, using Flask."""
import random
import json
import uuid
import pickle
import os
from pathlib import Path
from datetime import datetime

import yaml
import redis
from flask import Flask, render_template, request, jsonify, session
from flask import make_response

from ddt_core import DdtCore

app = Flask(__name__)
app.secret_key = "ddt-experiment-secret-key-change-in-production"

# Redis connection for multi-worker session storage
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0
)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/next_subject_id", methods=["GET"])
def next_subject_id():
    """Get the next available 4-digit subject ID by checking filesystem data directory"""
    try:
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        used_ids = set()
        for csv_file in data_dir.glob("*.csv"):
            filename = csv_file.name
            # Look for pattern DDT####_ses#_timestamp.csv
            if filename.startswith('DDT') and '_ses' in filename:
                try:
                    subject_id_str = filename[3:7]  # Extract 4 digits after DDT
                    if subject_id_str.isdigit():
                        used_ids.add(int(subject_id_str))
                except (ValueError, IndexError):
                    continue  # Skip files that don't match expected pattern
        
        # Find the next available 4-digit ID starting from 1001
        next_id = 1001
        while next_id in used_ids:
            next_id += 1
            if next_id > 9999:  # Safety check for 4-digit limit
                next_id = 1001
                break
        
        return jsonify({"next_subject_id": next_id})
        
    except Exception as e:
        # Return a default if there's an error
        return jsonify({"next_subject_id": 1001})


@app.route("/start", methods=["POST"])
def start():
    session_num = int(request.form.get("session"))
    num_train = int(request.form.get("num_train_trials"))
    num_main = int(request.form.get("num_main_trials"))
    show_tutorial = request.form.get("show_tutorial") == "1"

    # Generate unique session ID for this experiment
    session_id = str(uuid.uuid4())
    time_now_iso = datetime.now().isoformat().replace(":", "-")[:-7]
    path_data = Path(__file__).parent / "data"
    path_data.mkdir(exist_ok=True)

    # Handle subject ID assignment and file creation atomically
    subject_id_param = request.form.get("subject_id")
    if subject_id_param and subject_id_param.strip():
        # Use provided subject ID
        subject = int(subject_id_param)
        path_output = path_data / f"DDT{subject:04d}_ses{session_num}_{time_now_iso}.csv"
    else:
        # Use Redis for atomic subject ID assignment
        used_ids = set()
        for csv_file in path_data.glob("*.csv"):
            filename = csv_file.name
            # Look for pattern DDT####_ses#_timestamp.csv
            if filename.startswith('DDT') and '_ses' in filename:
                try:
                    subject_id_str = filename[3:7]  # Extract 4 digits after DDT
                    if subject_id_str.isdigit():
                        used_ids.add(int(subject_id_str))
                except (ValueError, IndexError):
                    continue  # Skip files that don't match expected pattern
        
        # Find the next available 4-digit ID starting from 1001
        subject = 1001
        while subject in used_ids:
            subject += 1
            if subject > 9999:  # Safety check for 4-digit limit
                subject = 1001
                break
        
        # Create the file path and immediately create placeholder file to reserve the ID
        path_output = path_data / f"DDT{subject:04d}_ses{session_num}_{time_now_iso}.csv"
        # Create empty file to reserve this subject ID immediately
        path_output.touch()

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

    # Store experiment data in Redis
    experiment_data = {
        "exp": exp,
        "config": config,
        "last_design": None,
        "created_at": datetime.now(),
    }
    redis_client.setex(f"session:{session_id}", 7200, pickle.dumps(experiment_data))

    return render_template("experiment.html", config_json=json.dumps(config))


@app.route("/next_design", methods=["GET"])
def next_design():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Session expired or invalid. Please refresh the page and start again."}), 400
    
    # Get experiment data from Redis
    exp_data_bytes = redis_client.get(f"session:{session_id}")
    if not exp_data_bytes:
        return jsonify({"error": "Session expired or invalid. Please refresh the page and start again."}), 400
    
    exp_data = pickle.loads(exp_data_bytes)
    exp = exp_data["exp"]

    mode = request.args.get("mode", "optimal")
    engine_mode = "random" if mode == "train" else mode
    design = exp.get_design(engine_mode)
    exp_data["last_design"] = design
    
    # Update Redis with new design
    redis_client.setex(f"session:{session_id}", 7200, pickle.dumps(exp_data))

    direction = random.randint(0, 1)
    return jsonify({"design": design, "direction": direction})


@app.route("/response", methods=["POST"])
def response():
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Session expired or invalid. Please refresh the page and start again."}), 400
    
    # Get experiment data from Redis
    exp_data_bytes = redis_client.get(f"session:{session_id}")
    if not exp_data_bytes:
        return jsonify({"error": "Session expired or invalid. Please refresh the page and start again."}), 400
    
    exp_data = pickle.loads(exp_data_bytes)
    exp = exp_data["exp"]
    config = exp_data["config"]
    last_design = exp_data["last_design"]

    mode = data.get("mode")
    if mode == "train":
        exp_data["last_design"] = None
        redis_client.setex(f"session:{session_id}", 7200, pickle.dumps(exp_data))
        return jsonify({"success": True})

    resp_left = int(data.get("resp_left"))
    direction = int(data.get("direction"))
    rt = float(data.get("rt"))
    resp_ss = resp_left if direction == 1 else 1 - resp_left

    exp.update_and_record(last_design, resp_ss, rt)
    exp_data["last_design"] = None

    finished = len(exp.df) >= config["num_main_trials"]
    if finished:
        exp.save_record()
        # Clean up completed experiment
        redis_client.delete(f"session:{session_id}")
    else:
        # Update Redis with cleared design
        redis_client.setex(f"session:{session_id}", 7200, pickle.dumps(exp_data))

    return jsonify({"finished": finished})


@app.before_request
def cleanup_old_sessions():
    """Clean up abandoned sessions older than 2 hours (handled by Redis TTL)."""
    # Redis TTL automatically handles cleanup, no action needed
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
