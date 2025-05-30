#!/bin/bash

# AWS DDT Setup Script
# This script sets up the necessary AWS resources for DDT deployment

set -e

echo "=== DDT AWS Setup ==="

# Get current AWS account ID and region
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=$(aws configure get region)
export BUCKET_NAME="3e.org"

echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Bucket: $BUCKET_NAME"

# Create S3 bucket if it doesn't exist
echo "Checking S3 bucket..."
if ! aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
    echo "Creating S3 bucket: $BUCKET_NAME"
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket $BUCKET_NAME
    else
        aws s3api create-bucket --bucket $BUCKET_NAME --create-bucket-configuration LocationConstraint=$AWS_REGION
    fi
    echo "✓ Created S3 bucket: $BUCKET_NAME"
else
    echo "✓ S3 bucket $BUCKET_NAME already exists"
fi

echo "✓ AWS setup complete!"
echo ""
echo "Next steps:"
echo "1. Run './deploy.sh' to deploy the DDT application"