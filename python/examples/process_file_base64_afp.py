# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a provided file via base64 encoding.


import base64
import os
import time
import requests

from python.helpers import process_file_helpers

PRIVATE_AI_URL = os.getenv('PAI_URL', 'http://localhost:8081')
USER_ID = os.getenv('USER_ID', "default")

file_name = "File Example PDF 1MB.pdf"
filepath = os.path.join("./data", file_name)

# Read from file
with open(filepath, "rb") as b64_file:
    file_data = base64.b64encode(b64_file.read()).decode()

request_data = {
    "file": {
        "data": file_data,
        "content_type": "application/pdf"
    }
}

print("Processing ", file_name, "...")
stt = time.time()
resp = requests.post(f"{PRIVATE_AI_URL}/process/files/base64", json=request_data, headers={"user-id": USER_ID})

if not resp.ok:
    print(f"Response for file {file_name} returned with {resp.status_code}")

# Get the job ID from the initial response
job_id = resp.json().get('job_id')

if not job_id:
    print("No job ID received. Unable to check status.")
    exit(1)

# Poll for job completion
while True:
    status_resp = requests.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID})
    if status_resp.ok:
        status_data = status_resp.json()
        print(f"Current status: {status_data['state']}")
        if status_data['state'] == 'completed':
            print("Redaction completed!")
            break
        elif status_data['state'] in ['failed', 'expired', 'cancelled']:
            print(f"Job failed with state: {status_data['state']}")
            print(f"Description: {status_data['description']}")
            exit(1)
    else:
        print(f"Failed to get job status. Status code: {status_resp.status_code}")
        exit(1)
    time.sleep(5)

process_file_helpers.download_file(job_id, file_name)

print(f"Total elapsed time: {time.time()-stt}")
