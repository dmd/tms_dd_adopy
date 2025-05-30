# DDT Experiment - Claude AI Assistant Guide

## Project Overview
This is a web-based Delayed Discounting Task (DDT) experiment using Flask and adaptive design optimization (ADO). The project was migrated from a PsychoPy desktop application to a modern web interface.

## Architecture

### Core Components
- **`ddt_core.py`** - Core experiment logic with ADOpy integration for adaptive design
- **`ddt_web.py`** - Flask web server handling HTTP requests and session management
- **`templates/`** - HTML templates for the web interface
- **`static/`** - CSS and JavaScript assets
- **`instructions.yml`** - Configurable experiment instructions
- **`data/`** - CSV output directory for experiment results

### Key Features
1. **Instant Crosshairs** - Immediate fixation cross feedback when users press keys
2. **Auto Subject ID Assignment** - Automatically assigns next available 4-digit ID (1001+)
3. **Form Lockdown** - All form fields are readonly/disabled to prevent user errors
4. **Setup Parameters** - URL parameter support for automated experiment configuration
5. **Session Management** - Thread-safe experiment state tracking with automatic cleanup

## File Structure
```
/Users/dmd/ddt/
├── ddt_core.py           # Core experiment logic
├── ddt_web.py            # Flask web application
├── instructions.yml      # Experiment instructions
├── readme.txt           # User documentation
├── requirements.txt     # Python dependencies
├── CLAUDE.md           # This file
├── data/               # Experiment output (CSV files)
├── templates/
│   ├── index.html      # Setup form
│   └── experiment.html # Experiment interface
└── static/
    ├── main.js         # Frontend JavaScript
    └── styles.css      # Styling
```

## Important Implementation Details

### Subject ID Management
- Subject IDs are 4-digit numbers starting from 1001
- The `/next_subject_id` endpoint scans existing CSV files in `data/` directory
- File naming pattern: `DDT{subject_id:04d}_ses{session}_{timestamp}.csv`
- Auto-assignment prevents ID conflicts

### Session Management
- Each experiment gets a unique UUID session ID
- Thread-safe storage in `experiments` dictionary with automatic cleanup
- Sessions expire after 2 hours of inactivity
- Experiment state includes ADO engine, configuration, and last design

### Frontend Behavior
- Instant crosshairs: Shows fixation cross immediately on key press
- Key bindings: 'z' (left), 'm'/'/' (right), space/Enter (instructions)
- Query parameter support for automation
- Form fields are locked by default for data integrity

### URL Parameters
- Individual: `?subject_id=1001&session=1&num_train_trials=5&num_main_trials=40&show_tutorial=1`
- Setup bundle: `?setup=1001,1,5,40,1` (subject_id,session,train_trials,main_trials,tutorial_flag)

## Development Commands

### Running the Application
```bash
python ddt_web.py
# Opens on http://localhost:5050/
```

### Dependencies
```bash
pip install -r requirements.txt
# Includes: Flask, ADOpy, numpy, pandas, scipy, PyYAML
```

### Testing
- Test the `/next_subject_id` endpoint to verify subject ID logic
- Verify form lockdown and auto-population work correctly
- Check instant crosshairs during trials
- Ensure CSV output format matches expectations

## Data Output
CSV files contain trial-by-trial data with ADO posterior estimates:
- Design parameters (delays, amounts)
- Response data (choice, reaction time)
- Posterior estimates (mean_k, mean_tau, sd_k, sd_tau)

## Migration Notes
- Successfully removed all PsychoPy dependencies
- Migrated from desktop to web-based interface
- Maintained ADO functionality and data format compatibility
- Added modern web features (instant feedback, automation support)

## Future Development
- The codebase is clean and modular
- Core logic in `ddt_core.py` is framework-agnostic
- Web interface can be easily extended or restyled
- Ready for deployment to cloud platforms if needed