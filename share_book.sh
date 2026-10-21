#!/bin/bash
set -euo pipefail

#check for missing arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <gutenberg_book_url> <bucket_name> <expiration_seconds>"
    exit 1
fi

#positional arguments
URL="$1"
BUCKET="$2"
EXPIRATION="$3"

#download the book
mkdir -p books
FILE="$(basename "$URL")"
curl -fsSL "$URL" -o "books/$FILE"

#create the bucket (unless it exists)
if aws s3 ls "s3://$BUCKET"> /dev/null 2>&1; then
     echo "The bucket $BUCKET already exists."
else
    aws s3 mb "s3://$BUCKET"
fi

#upload the book
aws s3 cp "books/$FILE" "s3://$BUCKET/$FILE" --content-type "text/plain; charset=utf-8"

#presign url to book and print
aws s3 presign "s3://$BUCKET/$FILE" --expires-in "$EXPIRATION"