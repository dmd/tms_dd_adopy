# DDT ADO Experiment - AWS Lambda Deployment

## Project Overview
This is a web-based Delay Discounting Task (DDT) experiment using Adaptive Design Optimization (ADO) deployed on AWS Lambda. The experiment presents participants with choices between immediate smaller rewards and delayed larger rewards to measure their discounting behavior.

## Architecture
- **Frontend**: HTML/JavaScript interface served from Lambda
- **Backend**: Python Flask application running on AWS Lambda
- **Storage**: 
  - S3 bucket `3e.org` for experiment data and session state
  - Session state stored in `ddt-sessions/` prefix
  - Final experiment results stored in `ddt-data/` prefix
- **Infrastructure**: AWS SAM for deployment management

## Key Files
- `ddt_web.py` - Main Flask application with Lambda handler
- `ddt_core.py` - Core experiment logic and ADO implementation
- `static/main.js` - Frontend experiment interface
- `templates/` - HTML templates for the web interface
- `aws-deploy/deploy.sh` - Non-interactive deployment script
- `aws-deploy/setup.sh` - Initial AWS infrastructure setup
- `.samignore` - Excludes development files from Lambda deployment

## Deployment Commands
```bash
# Initial setup (one-time)
cd aws-deploy
./setup.sh

# Deploy updates
./deploy.sh
```

## AWS Resources Created
- **Lambda Function**: `ddt-sam-app-DdtWebFunction-*`
- **API Gateway**: Provides public HTTPS endpoint
- **S3 Bucket**: `3e.org` for data storage
- **IAM Role**: Grants Lambda permissions for S3 read/write/delete

## Important Implementation Details

### Session Management
- Uses S3-based session storage (not in-memory) for Lambda statelessness
- Sessions stored as JSON in `s3://3e.org/ddt-sessions/{session_id}.json`
- Sessions auto-cleaned up after experiment completion
- Engine state restored from trial history using `restore_engine_state()`

### API Endpoints
- `GET /` - Main experiment interface
- `POST /start` - Initialize new experiment session
- `GET /next_design` - Get next trial parameters from ADO
- `POST /response` - Submit trial response and update ADO
- `GET /debug` - List active sessions (development)
- `GET /debug/{session_id}` - Debug specific session (development)

### S3 Permissions Required
The Lambda function needs these S3 permissions:
- `s3:GetObject` - Read session data and experiment files
- `s3:PutObject` - Write session data and experiment results  
- `s3:DeleteObject` - Clean up completed sessions
- `s3:ListBucket` - Debug endpoint functionality

### Known Issues & Solutions
1. **"Session expired" errors**: Fixed by implementing S3-based session storage
2. **403 Forbidden on API calls**: Fixed by adding `/Prod/` prefix to fetch URLs
3. **Import errors**: All required imports added at module level
4. **Memory limits**: Increased to 1024MB for ADO computations

## Development Workflow
1. Make changes to Python/JS files in main directory
2. Test locally if needed: `python ddt_web.py` (runs on port 5050)
3. Deploy to AWS: `cd aws-deploy && ./deploy.sh`
4. Test at: https://ueizal1w40.execute-api.us-east-1.amazonaws.com/Prod/

## Data Output
- Experiment results saved to `s3://3e.org/ddt-data/{filename}.csv`
- Format: Tab-separated CSV with trial-by-trial data
- Includes ADO posterior estimates and response times

## Testing & Debugging
- Use `/debug` endpoint to see active sessions
- Use `/debug/{session_id}` to test session loading
- Check CloudWatch logs: `aws logs tail /aws/lambda/ddt-sam-app-DdtWebFunction-* --since 5m`
- Verify S3 objects: `aws s3 ls s3://3e.org/ddt-sessions/`

## Dependencies
Key Python packages (see requirements.txt):
- flask - Web framework
- serverless-wsgi - Lambda integration  
- boto3 - AWS SDK
- pandas - Data manipulation
- adopy - Adaptive Design Optimization
- numpy, scipy - Scientific computing
- PyYAML - Configuration files

## Future Improvements
- Add authentication/authorization
- Implement session timeout cleanup
- Add experiment configuration via environment variables
- Consider using DynamoDB for session storage at scale
- Add monitoring and alerting