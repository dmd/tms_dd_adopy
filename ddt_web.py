#!/usr/bin/env python3
"""Web-based interface for the DDT ADO experiment, using Flask."""
import random
import json
from pathlib import Path
from datetime import datetime

import yaml
from flask import Flask, render_template, request, jsonify

from ddt_core import DdtCore

app = Flask(__name__)

exp = None
config = None
last_design = None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global exp, config
    subject = int(request.form.get('subject_id'))
    session = int(request.form.get('session'))
    num_train = int(request.form.get('num_train_trials'))
    num_main = int(request.form.get('num_main_trials'))
    show_tutorial = bool(request.form.get('show_tutorial'))
    time_now_iso = datetime.now().isoformat().replace(':','-')[:-7]
    path_data = Path(__file__).parent / 'data'
    path_data.mkdir(exist_ok=True)
    path_output = path_data / f'DDT{subject:03d}_ses{session}_{time_now_iso}.csv'
    exp = DdtCore(subject, session, path_output)
    instr_path = Path(__file__).parent / 'instructions.yml'
    with open(instr_path, 'r', encoding='utf-8') as f:
        instructions = yaml.safe_load(f)
    instructions['main_before'] = instructions['main_before'].format(num_main)
    config = {
        'subject_id': subject,
        'session': session,
        'num_train_trials': num_train,
        'num_main_trials': num_main,
        'show_tutorial': show_tutorial,
        'instructions': instructions,
    }
    return render_template('experiment.html', config_json=json.dumps(config))

@app.route('/next_design', methods=['GET'])
def next_design():
    global last_design
    mode = request.args.get('mode', 'optimal')
    engine_mode = 'random' if mode == 'train' else mode
    design = exp.get_design(engine_mode)
    last_design = design
    direction = random.randint(0, 1)
    return jsonify({'design': design, 'direction': direction})

@app.route('/response', methods=['POST'])
def response():
    global last_design, exp, config
    data = request.get_json()
    mode = data.get('mode')
    if mode == 'train':
        last_design = None
        return jsonify({'success': True})
    resp_left = int(data.get('resp_left'))
    direction = int(data.get('direction'))
    rt = float(data.get('rt'))
    resp_ss = resp_left if direction == 1 else 1 - resp_left
    exp.update_and_record(last_design, resp_ss, rt)
    last_design = None
    finished = len(exp.df) >= config['num_main_trials']
    if finished:
        exp.save_record()
    return jsonify({'finished': finished})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
