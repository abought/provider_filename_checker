#!/usr/bin/env bash
# Some of the filename tests can break an S3 bucket so badly that the web UI doesn't work properly.
# The offending files can be nuked via the CLI. This script nukes the entire bucket from orbit but can be refined.

# Refs http://docs.aws.amazon.com/AmazonS3/latest/dev/delete-or-empty-bucket.html#empty-bucket

# Run `aws configure` first to provide credentials, then run this as ./aws_fixer.sh <bucketname>
if [ -z "$1" ]; then
    echo 'Please specify a bucket name (or bucket/folder to be more granular)';
    exit 1;
fi

read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
    echo "Emptying all contents of AWS bucket $1";
    aws s3 rm "s3://$1" --recursive
fi
