import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PRIVATE_AI_URL = os.getenv('PAI_URL')
USER_ID = os.getenv('USER_ID')

def get_status(job_id):
    status_resp = requests.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID})
    if status_resp.ok:
        status_data = status_resp.json()
        print(f"Current status: {status_data['state']}")
        if status_data['state'] in ['completed', 'downloaded']:
            return True
        elif status_data['state'] in ['failed', 'expired', 'cancelled']:
            print(f"Job failed with state: {status_data['state']}")
            print(f"Description: {status_data['description']}")
            return False
    else:
        print(f"Failed to get job status. Status code: {status_resp.status_code}")
        print(f"Error message: {status_resp.text}")
        return False

def download_file(job_id, file_name):
    download_url = f"{PRIVATE_AI_URL}/jobs/{job_id}"
    download_resp = requests.get(download_url, headers={"user-id": USER_ID})

    if download_resp.ok:
        try:
            with open(os.path.join("./output", f"Redacted {file_name}"), 'wb') as redacted_file:
                processed_file = download_resp.json().get('processed_file')
                
                if processed_file is None:
                    raise ValueError("No processed file data found in the response")
                
                try:
                    decoded_file = base64.b64decode(processed_file, validate=True)
                except base64.binascii.Error as e:
                    print(f"Error decoding base64 data: {e}")
                    raise
                
                redacted_file.write(decoded_file)
            print(f"Successfully downloaded redacted file: Redacted {file_name}")
        except IOError as e:
            print(f"Error writing to file: {e}")
        except ValueError as e:
            print(f"Error processing response data: {e}")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
    else:
        print(f"Failed to download redacted file. Status code: {download_resp.status_code}")