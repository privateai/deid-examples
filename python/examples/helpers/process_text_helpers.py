import base64
import os
import aiofiles
import aiohttp
import requests
from dotenv import load_dotenv
from aiohttp import ClientSession

load_dotenv()

PRIVATE_AI_URL = os.getenv('PAI_URL')
USER_ID = os.getenv('USER_ID')
INPUT_DIR_PATH = "./data"
OUTPUT_DIR_PATH = "./output"

def submit_job(text_array, LINK_BATCH):
    request_data = {
        "text": text_array,
        "link_batch": LINK_BATCH
    }

    print("Processing text...")

    resp = requests.post(f"{PRIVATE_AI_URL}/process/text", json=request_data, headers={"user-id": USER_ID})

    if not resp.ok:
        print(f"Response for text returned with {resp.status_code}")
    else:
        # Get the job ID
        job_id = resp.json().get('job_id')

        if not job_id:
            print(f"No job ID received")
            return None

        return job_id

async def get_status(job_id):
    async with ClientSession() as session:
        async with session.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID}) as status_resp:
            if status_resp.status == 200:
                status_data = await status_resp.json()
                print(f"Current status: {status_data['state']}")
                if status_data['state'] in ['completed', 'downloaded']:
                    return True
                elif status_data['state'] in ['failed', 'expired', 'cancelled']:
                    print(f"Deidentification failed with state: {status_data['state']}")
                    print(f"Description: {status_data['description']}")
                    return False
            else:
                print(f"Failed to get job status. Status code: {status_resp.status}")
                print(f"Error message: {await status_resp.text()}")
                return False

async def return_text(job_id):
    async with ClientSession() as session:
        download_url = f"{PRIVATE_AI_URL}/jobs/{job_id}"
        async with session.get(download_url, headers={"user-id": USER_ID}) as download_resp:
            if download_resp.status == 200:
                try:
                    response_data = await download_resp.json()
                    processed_text = []
                    for text in response_data:
                        processed_text.append(text.get('processed_text'))
                    
                    if processed_text is None:
                        raise ValueError("No processed text data found in the response")
                
                    print(f"Successfully redacted text: {processed_text}")
                except ValueError as e:
                    print(f"Error processing response data: {e}")
                except Exception as e:
                    print(f"Unexpected error occurred: {e}")
            else:
                print(f"Failed to return redacted text. Status code: {download_resp.status}")
