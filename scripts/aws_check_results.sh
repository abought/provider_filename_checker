#!/usr/bin/env bash

# Some of these file name tests may break the AWS S3 web console. This script allows a user to see contents of the bucket.

# Run `aws configure` first to provide credentials, then run this as ./aws_check_results.sh <bucketname>
if [ -z "$1" ]; then
    echo 'Please specify a bucket name';
    exit 1;
fi

aws s3 ls "s3://$1" --recursive
