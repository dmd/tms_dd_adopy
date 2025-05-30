# DDT ADO Experiment - AWS Lambda Deployment

## Overview
This is a web-based Delay Discounting Task (DDT) experiment using Adaptive Design Optimization (ADO) designed for deployment on AWS Lambda. The experiment presents participants with choices between immediate smaller rewards and delayed larger rewards to measure their discounting behavior.

## Architecture
- **Frontend**: HTML/JavaScript interface served from Lambda
- **Backend**: Python Flask application running on AWS Lambda  
- **Storage**: S3 bucket `3e.org` for experiment data and session state
- **Infrastructure**: AWS SAM for deployment management

## Deployment (Primary Usage)
This version is specifically designed for AWS Lambda deployment:

```bash
# Initial setup (one-time)
cd aws-deploy
./setup.sh

# Deploy updates  
./deploy.sh
```


## Experiment Features
- **Form Lockdown**: All form fields are readonly to prevent parameter tampering
- **Query Parameter Support**: URL supports individual parameters (subject_id, session, train_trials, main_trials, tutorial)
- **Setup Parameter**: Single `setup` parameter with 5 comma-separated values overrides individual parameters
- **Automatic Subject ID**: `/next_subject_id` endpoint assigns next available 4-digit ID (starting from 1001)
- **Data Retrieval**: `/data/{subject_id}/{session}` endpoint provides direct CSV download

## API Endpoints
- `GET /` - Main experiment interface
- `POST /start` - Initialize new experiment session
- `GET /next_design` - Get next trial parameters from ADO
- `POST /response` - Submit trial response and update ADO
- `GET /next_subject_id` - Get next available subject ID from S3 data
- `GET /data/{subject_id}/{session}` - Retrieve experiment data as CSV (returns most recent if multiple files exist)
- `GET /debug` - List active sessions (development)

## Session Management
- Uses S3-based session storage for Lambda statelessness
- Sessions stored as JSON in `s3://3e.org/ddt-sessions/{session_id}.json`
- Sessions auto-cleaned up after experiment completion
- Engine state restored from trial history using `restore_engine_state()`

## Data Format
Data are saved in csv format.
The columns in a csv file will be as below:

-subject: subject code
-block: block number
-block_type: fixed as ado in this task
-trial: trial number
-t_ss: delay of shorter-smaller option (always zero)
-t_ll: delay of longer-larger option (in weeks)
-r_ss: amount of shorter-smaller reward
-r_ll: amount of longer-larger reward
-resp_ss: response in the trial (0 = ll, 1 = ss)
-rt: response time (in seconds)
-mean_k: posterior mean of the delay discounting rate parameter (hyperbolic model)
-mean_tau: posterior mean of the tau parameter
-sd_k: standard deviation of the delay discounting rate parameter
-sd_tau: standard deviation of the tau parameter
