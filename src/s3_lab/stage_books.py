import logging
import os
import boto3
import argparse
import requests

from botocore.exceptions import ClientError

list_file = 'book_urls.txt'
index_path = 'index.html'
bucket = 'public-mst3k'

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
    os.makedirs(dest_dir, exist_ok=True)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # raise an error for 404 etc.
        # save response.content to the file
    except requests.RequestException as e:
        log.error(f"Error downloading {url}: {e}")
    print(1)

def create_bucket(bucket):
    """Creates a bucket. Returns True if the nucket exists afterwards and False otherwise."""
    log.info(f"{bucket}")
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        # us-east-1: omit LocationConstraint or create_bucket fails
        s3.create_bucket(Bucket=bucket)
        log.info(f"Created bucket: {bucket}")
    except ClientError as e:
        log.error(f"Error creating bucket {bucket}: {e}")

def make_public(bucket):
    print(1)

def upload_files(bucket, file_paths):
    try:
        s3 = boto3.client("s3")
        with open(file_paths, "rb") as f:
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=f,
                ContentType="image/jpeg",  # so browsers can display, not download
            )
            log.info(f"Uploaded {file_paths} to s3://{bucket}/{key}")
    except FileNotFoundError:
        log.error(f"Local file not found: {file_paths}")
    except ClientError as e:
        log.error(f"Error uploading object: {e}")

def upload_index(bucket, index_path):
    print(1)

def main():
    print(1)