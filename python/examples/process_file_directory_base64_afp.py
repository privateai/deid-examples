# Example script to illustrate how to make API calls to the Private AI API
# to deidentify all files in a provided directory.

import base64
import time
import os
import requests

from os import listdir
from os.path import isfile, join
from helpers import process_file_helpers
# from python.data.file_types import SUPPORTED_FILE_TYPES
from dotenv import load_dotenv

load_dotenv()

PRIVATE_AI_URL = os.getenv('PAI_URL')
USER_ID = os.getenv('USER_ID')
INPUT_DIR_PATH = "./data"
OUTPUT_DIR_PATH = "./output"

SUPPORTED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".json": "application/json",
    ".xml": "application/xml",
    ".csv": "text/csv",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".eml": "message/rfc822",
    ".txt": "text/plain",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".dcm": "application/dicom",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".png": "image/png",
    ".bmp": "image/bmp",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".m4a": "audio/m4a",
    ".webm": "audio/webm",
}

# Gather all files in directory
files = [file for file in listdir(INPUT_DIR_PATH) if isfile(join(INPUT_DIR_PATH, file))]

# Class for jobs for job_queue
class jobs:
    def __init__(self, job_id, file_name):
        self.job_id = job_id
        self.file_name = file_name

job_queue = []

# Start timer
stt = time.time()

for file_name in files:

    file_ext = file_name[file_name.rfind("."):] # Gets the file extension

    if file_ext in SUPPORTED_FILE_TYPES:
        filepath = os.path.join(INPUT_DIR_PATH, file_name)
        file_type = SUPPORTED_FILE_TYPES[file_ext]

        # Read from file
        with open(filepath, "rb") as b64_file:
            file_data = base64.b64encode(b64_file.read()).decode()

        request_data = {
            "file": {
                "data": file_data,
                "content_type": file_type,
            }
        }

        print("Processing ", file_name, "...")

        resp = requests.post(f"{PRIVATE_AI_URL}/process/files/base64", json=request_data, headers={"user-id": USER_ID})

        if not resp.ok:
            print(f"Response for file {file_name} returned with {resp.status_code}")
        else:
            # Get the job ID
            job_id = resp.json().get('job_id')

            if not job_id:
                print(f"No job ID received for {file_name}")
                continue
            
            job_queue.append(jobs(job_id, file_name)) 
    else:
        print(f"File {file_name} not supported and will not be deidentified.")

# Poll for job completion
while job_queue:

    for job in job_queue:
        status_resp = requests.get(f"{PRIVATE_AI_URL}/jobs/{job.job_id}/state", headers={"user-id": USER_ID})

        if status_resp.ok:
            status_data = status_resp.json()
            print(f"{job.file_name} current status: {status_data['state']}")

            if status_data['state'] == 'completed':
                # Download the redacted file
                process_file_helpers.download_file(job.job_id, job.file_name)

                # Remove job from queue
                job_queue.remove(job)

            elif status_data['state'] in ['failed', 'expired', 'cancelled']:
                print(f"Deidentification of {job.file_name} failed with state: {status_data['state']}")
                print(f"Description: {status_data['description']}")

                # Remove job from queue
                job_queue.remove(job)
        else:
            print(f"Failed to get {job.file_name} job status. Status code: {status_resp.status_code}")

            # Remove job from queue
            job_queue.remove(job)

    time.sleep(5)

# Calculate and display total elapsed time
elapsed_time = time.time() - stt
minutes, seconds = divmod(int(elapsed_time), 60)
print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")