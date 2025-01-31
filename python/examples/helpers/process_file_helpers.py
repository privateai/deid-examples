import base64
import os
import aiofiles
import aiohttp
import requests
from dotenv import load_dotenv
from aiohttp import ClientSession

from constants.file_types import SUPPORTED_FILE_TYPES

load_dotenv()

PRIVATE_AI_URL = os.getenv('PAI_URL')
USER_ID = os.getenv('USER_ID')
INPUT_DIR_PATH = "./data"
OUTPUT_DIR_PATH = "./output"

# Class for jobs in job_queue
class jobs:
    def __init__(self, job_id, file_name):
        self.job_id = job_id
        self.file_name = file_name

def submit_job(file_name):
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
                return None

            return job_id
    else:
        print(f"File {file_name} not supported and will not be deidentified.")
        return None

async def get_status(job_id, file_name):
    async with ClientSession() as session:
        async with session.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID}) as status_resp:
            if status_resp.status == 200:
                status_data = await status_resp.json()
                print(f"{file_name} current status: {status_data['state']}")
                if status_data['state'] in ['completed', 'downloaded']:
                    return True
                elif status_data['state'] in ['failed', 'expired', 'cancelled']:
                    print(f"Deidentification of {file_name} failed with state: {status_data['state']}")
                    print(f"Description: {status_data['description']}")
                    return False
            else:
                print(f"Failed to get {file_name} job status. Status code: {status_resp.status}")
                print(f"Error message: {await status_resp.text()}")
                return False

async def download_file(job_id, file_name):
    async with ClientSession() as session:
        download_url = f"{PRIVATE_AI_URL}/jobs/{job_id}"
        async with session.get(download_url, headers={"user-id": USER_ID}) as download_resp:
            if download_resp.status == 200:
                try:
                    response_data = await download_resp.json()
                    processed_file = response_data.get('processed_file')
                    
                    if processed_file is None:
                        raise ValueError("No processed file data found in the response")
                    
                    try:
                        decoded_file = base64.b64decode(processed_file, validate=True)
                    except base64.binascii.Error as e:
                        print(f"Error decoding base64 data: {e}")
                        raise
                    
                    output_path = os.path.join("./output", f"Redacted {file_name}")
                    async with aiofiles.open(output_path, 'wb') as redacted_file:
                        await redacted_file.write(decoded_file)
                    print(f"Successfully downloaded redacted file: Redacted {file_name}")
                except IOError as e:
                    print(f"Error writing to file: {e}")
                except ValueError as e:
                    print(f"Error processing response data: {e}")
                except Exception as e:
                    print(f"Unexpected error occurred: {e}")
            else:
                print(f"Failed to download redacted file. Status code: {download_resp.status}")
