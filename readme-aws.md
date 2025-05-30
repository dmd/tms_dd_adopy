# AWS Lambda Deployment Guide

This guide explains how to deploy the DDT web application to AWS Lambda using AWS SAM.

## Prerequisites

- AWS CLI configured via `aws configure sso`
- AWS SAM CLI installed ([installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Python 3.8+
- AWS account with Lambda, S3, and API Gateway access

## Deployment Steps

### 1. Initial AWS Setup

Run the setup script to create the required S3 bucket:

```bash
cd aws-deploy
./setup.sh
```

This script will:
- Check your AWS account ID and region
- Create the S3 bucket `3e.org` if it doesn't exist
- Verify your AWS credentials are working

### 2. Deploy the Application

Run the deployment script:

```bash
./deploy.sh
```

This script will:
- Generate a secure secret key for Flask sessions
- Create a SAM template with your account details
- Build and deploy the application using `sam deploy --guided`
- Set up Lambda function, API Gateway, and IAM roles automatically

### 3. Access Your Application

After deployment completes, SAM will output the API Gateway URL where your DDT application is accessible.

## What Gets Created

The deployment creates:
- **Lambda Function**: Runs the DDT web application
- **API Gateway**: Provides HTTP access to the Lambda function
- **IAM Role**: Allows Lambda to write to S3 and CloudWatch logs
- **S3 Bucket**: Stores experiment data files at `3e.org/ddt-data/`

## Data Storage

Completed experiment data is automatically uploaded to:
- **Bucket**: `3e.org`
- **Path**: `ddt-data/{filename}.csv`
- **Format**: Tab-separated CSV files

## Monitoring

Monitor your application through:
- **CloudWatch Logs**: Application logs and errors
- **CloudWatch Metrics**: Performance and usage metrics
- **S3 Console**: View uploaded experiment data

## Updating the Application

To update your deployed application:

1. Make changes to your code
2. Run `./deploy.sh` again
3. SAM will update the existing resources

## Troubleshooting

- **Cold starts**: First requests may be slower due to Lambda initialization
- **Memory limits**: Default is 512MB; increase in template.yaml if needed
- **Timeout errors**: Default timeout is 30 seconds; adjust if needed
- **S3 permissions**: Verify the Lambda role has write access to the S3 bucket

## Clean Up

To remove all AWS resources:

```bash
sam delete
```

This will delete the CloudFormation stack and all associated resources.