# %%

import datetime
import json
import os

import boto3
import requests

# SUBJECT DATE ### TRY A FEW OF THIS IN CLASS - INSTRUCTONS WILL COME FROM THE INSTRUCTOR
# DATE_PARAM = "2023-10-15"
# DATE_PARAM = "2023-10-16"
# DATE_PARAM = "2023-10-17"
# DATE_PARAM = "2023-10-18"
# DATE_PARAM = "2023-10-19"
# DATE_PARAM = "2023-10-20"
DATE_PARAM = "2023-10-21"

date = datetime.datetime.strptime(DATE_PARAM, "%Y-%m-%d")

# Wikimedia API URL formation
url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date.strftime('%Y/%m/%d')}"
print(f"Requesting REST API URL: {url}")

# Getting response from Wikimedia API
wiki_server_response = requests.get(url, headers={"User-Agent": "curl/7.68.0"})
wiki_response_status = wiki_server_response.status_code
wiki_response_body = wiki_server_response.text

print(f"Wikipedia REST API Response body: {wiki_response_body}")
print(f"Wikipedia REST API Response Code: {wiki_response_status}")

# Check if response status is not OK
if wiki_response_status != 200:
    print(
        f"Received non-OK status code from Wiki Server: {wiki_response_status}. Response body: {wiki_response_body}"
    )

# %%
# Save Raw Response and upload to S3
from pathlib import Path

## Get the directory of the current file
current_directory = Path(__file__).parent

# Path for the new directory
RAW_LOCATION_BASE = current_directory / "data" / "raw-views"

# Create the new directory, ignore if it already exists
RAW_LOCATION_BASE.mkdir(exist_ok=True, parents=True)
print(f"Created directory {RAW_LOCATION_BASE}")

# %%

# Save the contents of `wiki_response_body` to file called `raw-edits-YYYY-MM-DD.txt` into the folder
# in variable `RAW_LOCATION_BASE` defined
raw_views_file = RAW_LOCATION_BASE / f"raw-views-{date.strftime('%Y-%m-%d')}.txt"
with raw_views_file.open("w") as file:
    file.write(wiki_response_body)
    print(f"Saved raw views to {raw_views_file}")


# %%

s3 = boto3.client("s3")
S3_WIKI_BUCKET = "ceu-jo-kudo-wikidata"


bucket_names = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
# Only create the bucket if it doesn't exist
if S3_WIKI_BUCKET not in bucket_names:
    s3.create_bucket(
        Bucket=S3_WIKI_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )

# Check your solution
assert S3_WIKI_BUCKET != "", "Please set the S3_WIKI_BUCKET variable"
assert s3.list_objects(
    Bucket=S3_WIKI_BUCKET
), "The bucket {S3_WIKI_BUCKET} does not exist"

# %%

# Upload the file you created to S3.

print(raw_views_file)
res = s3.upload_file(
    raw_views_file,
    S3_WIKI_BUCKET,
    f"datalake/raw/raw-views-{date.strftime('%Y-%m-%d')}.txt",
)
print(
    f"Uploaded raw views to s3://{S3_WIKI_BUCKET}/datalake/raw/raw-views-{date.strftime('%Y-%m-%d')}.txt"
)

assert s3.head_object(
    Bucket=S3_WIKI_BUCKET,
    Key=f"datalake/raw/raw-views-{date.strftime('%Y-%m-%d')}.txt",
)



# %%
# Parse the Wikipedia response and process the data
print("wiki_server_response= ", wiki_server_response)
wiki_response_parsed = wiki_server_response.json()


top_edits = wiki_response_parsed["items"][0]["articles"]

# Convert server's response to JSON lines
current_time = datetime.datetime.utcnow()  # Always use UTC!!
json_lines = ""
for page in top_edits:
    record = {
        "article": page["article"],
        "views": page["views"],
        "ranks": page["rank"],
        "date": date.strftime("%Y-%m-%d"),
        "retrieved_at": current_time.isoformat(),
    }
    json_lines += json.dumps(record) + "\n"

# Save the Top Edits JSON lines and upload them to S3
JSON_LOCATION_DIR = current_directory / "data" / "views"
JSON_LOCATION_DIR.mkdir(exist_ok=True, parents=True)
print(f"Created directory {JSON_LOCATION_DIR}")
print(f"JSON lines:\n{json_lines}")

# %%
json_lines_filename = f"views-{date.strftime('%Y-%m-%d')}.json"
json_lines_file = JSON_LOCATION_DIR / json_lines_filename

with json_lines_file.open("w") as file:
    file.write(json_lines)

# Upload the JSON file
s3.upload_file(json_lines_file, S3_WIKI_BUCKET, f"datalake/views/{json_lines_filename}")
print(
    f"Uploaded JSON lines to s3://{S3_WIKI_BUCKET}/datalake/views/{json_lines_filename}"
)
