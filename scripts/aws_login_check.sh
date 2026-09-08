#!/bin/bash

echo "======================================"
echo " AWS Login & Environment Check"
echo "======================================"

echo ""
echo "1. Checking AWS CLI installation..."
aws --version

echo ""
echo "2. Checking authenticated AWS identity..."
aws sts get-caller-identity

echo ""
echo "3. Checking configured AWS region..."
aws configure get region

echo ""
echo "AWS environment check complete."