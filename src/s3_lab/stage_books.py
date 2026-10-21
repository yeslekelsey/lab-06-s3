#!/usr/bin/env python3

import logging
import os
import boto3
import time
import json
import argparse
import requests
import sys

from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

s3 = boto3.client("s3", region_name="us-east-1")

def parse_args():
    """Read the command line arguments"""
    parser = argparse.ArgumentParser(
        description="Stage Project Gutenberg books in a public S3 bucket."
    )
    parser.add_argument("list_file", help="Path to the book URL list")
    parser.add_argument("index_path", help="Path to the index page")
    parser.add_argument("bucket", help="Name of the public bucket")
    args = parser.parse_args()
    return args.list_file, args.index_path, args.bucket

def download_books(list_file, dest_dir):
    """Downloads a list of books and saves in in a directory."""
    os.makedirs(dest_dir, exist_ok=True)
    paths = []
    with open(list_file) as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        path = os.path.join(dest_dir, url.split("/")[-1]) #get path
        if os.path.exists(path):
            log.info(f"{path} is already downloaded")
            paths.append(path)
            continue
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # raise an error for 404 etc.
            with open(path, "wb") as out:
                out.write(response.content)
            log.info(f"Downloaded {url} to {path}")
            paths.append(path)
        except requests.RequestException as e:
            log.error(f"Error downloading {url}: {e}")
        time.sleep(1)
        return paths
    
    

def create_bucket(bucket):
    """Creates a bucket. Returns True if the bucket exists afterwards and False otherwise."""
    log.info(f"{bucket}")
    #check if bucket exists first:
    try:
        s3.head_bucket(Bucket=bucket)
        log.info(f"Bucket {bucket} already exists")
        return True
    except:
        pass # create it below
    try:
        s3.create_bucket(Bucket=bucket)
        log.info(f"Created bucket: {bucket}")
        return True
    except ClientError as e:
        log.error(f"Error creating bucket {bucket}: {e}")
        return False

def make_public(bucket):
    """Turn off Block Public Access for the bucket, then attach a bucket policy that allows anyone to read its objects."""
    try:
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False,
        },
        )

        policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket}/*"
            }
        ]
        }

        s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))

        log.info(f"Made bucket {bucket} public")
        return True
    except ClientError as e:
        log.error(f"Error making bucket {bucket} public: {e}")
        return False

def upload_files(bucket, file_paths):
    """Loops over file_paths and uploads each file to the top level of the bucket. Returns the number of files uploaded successfully."""
    
    uploaded = 0
    for path in file_paths:
        key = os.path.basename(path)
        try:
            with open(path, "rb") as f:
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=f,
                    ContentType="text/plain; charset=utf-8",
                )
            log.info(f"Uploaded {path} to s3://{bucket}/{key}")
            uploaded += 1
        except FileNotFoundError:
            log.error(f"Local file not found: {path}")
        except ClientError as e:
            log.error(f"Error uploading {path}: {e}")
    log.info(f"Uploaded {uploaded} of {len(file_paths)} files")
    return uploaded

def upload_index(bucket, index_path):
    """Loop over the files in a path and upload to a bucket"""
    try:
        with open(index_path, "rb") as f:
            s3.put_object(
                Bucket=bucket,
                Key="index.html",
                Body=f,
                ContentType="text/html",  # so browsers can display as a web page
            )
        log.info(f"Uploaded {index_path} to s3://{bucket}/{"index.html"}")
        return True
    except FileNotFoundError:
        log.error(f"Local file not found: {index_path}")
        return False
    except ClientError as e:
        log.error(f"Error uploading object: {e}")
        return False

def main():
    """Download books, creat/publish bucket, and upload everything"""
    list_file, index_path, bucket = parse_args()
    file_paths = download_books(list_file, "books")
    
    if not file_paths: #can't download books
        log.error("No books were downloaded")
        sys.exit(1)

    if not create_bucket(bucket) or not make_public(bucket):
        log.error(f"Could not create or publish bucket {bucket}")
        sys.exit(1)

    if not 
    
    count = upload_files(bucket, file_paths)
    if upload_index(bucket, index_path) and count == len(file_paths):
        log.info("All books and index page were updated :)")
    else:
        log.error("Some updates failed: check the log")
    log.info(f"Index page: https://{bucket}.s3.amazonaws.com/index.html")

    

if __name__ == "__main__":
    main()