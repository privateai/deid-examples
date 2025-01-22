import base64
import os
import requests

PRIVATE_AI_URL = os.getenv('PAI_URL', 'http://localhost:8081')

def download_file(job_id, file_name):
    download_url = f"{PRIVATE_AI_URL}/jobs/{job_id}"
    download_resp = requests.get(download_url, headers={"user-id": "michelle"})

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