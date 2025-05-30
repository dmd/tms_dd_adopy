#!/bin/bash

# AWS DDT Deployment Script
# This script deploys the DDT application using AWS SAM

set -e

echo "=== DDT AWS Deployment ==="

# Check if SAM is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first:"
    echo "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Get current AWS account details
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=$(aws configure get region)
export BUCKET_NAME="3e.org"

echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"

# Generate SAM template
echo "Generating SAM template..."
cat > template.yaml << EOF
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  DdtWebFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ..
      Handler: ddt_web.lambda_handler
      Runtime: python3.9
      Timeout: 30
      MemorySize: 3008
      Environment:
        Variables:
          SECRET_KEY: "flask-secret-key-for-lambda"
      Policies:
        - S3WritePolicy:
            BucketName: $BUCKET_NAME
        - Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Action:
                - s3:GetObject
                - s3:ListBucket
                - s3:DeleteObject
              Resource: 
                - "arn:aws:s3:::$BUCKET_NAME"
                - "arn:aws:s3:::$BUCKET_NAME/*"
            - Effect: Allow
              Action:
                - logs:CreateLogGroup
                - logs:CreateLogStream
                - logs:PutLogEvents
              Resource: "arn:aws:logs:$AWS_REGION:$AWS_ACCOUNT_ID:*"
      Events:
        ApiRoot:
          Type: Api
          Properties:
            Path: /
            Method: ANY
        ApiProxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Outputs:
  DdtWebApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://\${ServerlessRestApi}.execute-api.$AWS_REGION.amazonaws.com/Prod/"
  DdtWebFunction:
    Description: "DDT Lambda Function ARN"
    Value: !GetAtt DdtWebFunction.Arn
EOF

echo "✓ Generated template.yaml"

# Build and deploy
echo "Building SAM application..."
sam build

echo "Deploying SAM application..."
sam deploy --stack-name ddt-sam-app --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset

echo "✓ Deployment complete!"
echo ""
echo "Your DDT application is now deployed to AWS Lambda."
echo "Check the CloudFormation stack outputs for the API Gateway URL."