import boto3
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize S3 client using configured AWS region
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))

BUCKET = os.getenv("S3_BUCKET_NAME")
TRACK_FILE = os.getenv("TRACK_FILE", "uploaded_file_hashes.json")

# Files monitored for S3 sync
FILES = [
    {
        "local_path": os.getenv("PARTS_LOCAL_PATH"),
        "s3_key": os.getenv("PARTS_S3_KEY")
    },
    {
        "local_path": os.getenv("PLANNERS_LOCAL_PATH"),
        "s3_key": os.getenv("PLANNERS_S3_KEY")
    },
    {
        "local_path": os.getenv("ADDRESSES_LOCAL_PATH"),
        "s3_key": os.getenv("ADDRESSES_S3_KEY")
    }
]


def file_hash(path):
    # Generate file hash to detect content changes
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


def load_hashes():
    # Load previously uploaded file hashes
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return json.load(f)

    return {}


def save_hashes(hashes):
    # Persist latest file hashes after successful uploads
    with open(TRACK_FILE, "w") as f:
        json.dump(hashes, f, indent=2)


def upload_changed_files():
    # Upload only files whose content changed since the last sync
    if not BUCKET:
        return {
            "changed_count": 0,
            "message": "S3_BUCKET_NAME is missing. Add it to your .env file."
        }

    uploaded_hashes = load_hashes()
    changed_count = 0

    for item in FILES:
        local_path = item["local_path"]
        s3_key = item["s3_key"]

        if not local_path or not s3_key:
            continue

        if not os.path.exists(local_path):
            print(f"Missing file: {local_path}")
            continue

        current_hash = file_hash(local_path)

        # Skip upload if file content has not changed
        if uploaded_hashes.get(local_path) == current_hash:
            print(f"Skipped unchanged file: {local_path}")
            continue

        # Upload updated file to S3
        s3.upload_file(local_path, BUCKET, s3_key)

        uploaded_hashes[local_path] = current_hash
        changed_count += 1

        print(f"Uploaded new/changed file: {local_path} → s3://{BUCKET}/{s3_key}")

    save_hashes(uploaded_hashes)

    if changed_count == 0:
        return {
            "changed_count": 0,
            "message": "No new/changed files. S3 not updated. Lambda not triggered."
        }

    return {
        "changed_count": changed_count,
        "message": f"{changed_count} file(s) uploaded. S3 Lambda will trigger."
    }