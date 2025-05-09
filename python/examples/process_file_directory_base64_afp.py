import base64
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

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

load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in your environment to run the examples.")
if "USER_ID" not in os.environ:
    raise KeyError("USER_ID must be defined in your environment to run the examples.")

PRIVATE_AI_URL = os.getenv("PAI_URL")
USER_ID = os.getenv("USER_ID")

INPUT_DIR_PATH = "./data"
OUTPUT_DIR_PATH = "./output"


def get_file_request(file_name: str) -> dict:
    # Opening file to build request json
    _, ext = os.path.splitext(file_name)

    if ext not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"File type {ext} not supported and will not be deidentified.")
    else:
        filepath = os.path.join(INPUT_DIR_PATH, file_name)
        file_type = SUPPORTED_FILE_TYPES[ext]

        # Read from file
        with open(filepath, "rb") as b64_file:
            file_data = base64.b64encode(b64_file.read()).decode()

        return {
            "file": {
                "data": file_data,
                "content_type": file_type,
            }
        }


def check_status(response: requests.Response) -> None:
    if not response.ok:
        print(f"Unexpected response: {response.status_code} - {response.text}")
        response.raise_for_status()


def submit_job(file_request: dict) -> str:
    response = requests.post(f"{PRIVATE_AI_URL}/process/files/base64", json=file_request, headers={"user-id": USER_ID})
    check_status(response)

    # Get the job ID
    job_id = response.json().get("job_id")

    return job_id


def get_state(job_id: str) -> tuple[str, str]:
    session = requests.Session()
    with session.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID}) as response:
        check_status(response)
        response_data = response.json()
        return response_data.get("state"), response_data.get("description")


def download_file(job_id: str, output_file_name: str) -> None:
    with requests.get(f"{PRIVATE_AI_URL}/jobs/{job_id}", headers={"user-id": USER_ID}) as response:
        check_status(response)

        processed_file = response.json().get("processed_file")

        decoded_file = base64.b64decode(processed_file, validate=True)

        output_path = os.path.join("./output", f"Redacted {output_file_name}")
        with open(output_path, "wb") as redacted_file:
            redacted_file.write(decoded_file)

        print(f"Successfully downloaded redacted file: Redacted {output_file_name}")


def process_file(file_name: str) -> tuple[str, str, str]:

    if file_name.lower() == ".ds_store":  # skip the desktop services store on macs
        print(f"Skipping {file_name}")
        return

    print(f"Processing {file_name}")
    request_data = get_file_request(file_name)

    # Submit file for processing and get job id
    job_id = submit_job(request_data)

    # Poll for job completion
    while True:
        state, description = get_state(job_id)
        if state in ["completed", "downloaded"]:
            print(f"Deidentification of {file_name} finished")
            break
        elif state in ["failed", "expired", "cancelled"]:
            print(f"Deidentification of {file_name} failed with description: {description}")
            return job_id, file_name, state
        else:
            print(f"Deidentification of {file_name} state: {state}")
        time.sleep(5)

    # Download deidentified file
    download_file(job_id, output_file_name=f"redacted-{file_name}")
    return job_id, file_name, state


def process_directory(directory: str) -> None:
    # Gather all files in directory
    files = os.listdir(directory)
    # Submit files for processing, one thread for each
    with ThreadPoolExecutor(max_workers=5) as executor:

        futures = []
        results = []
        for file in files:
            futures.append(executor.submit(process_file, file))
        for future in as_completed(futures):
            results.append(future.result())

    for result in results:
        print(f"job_id: {result[0]}, file: {result[1]}, state: {result[2]}")


if __name__ == "__main__":

    # Start timer
    stt = time.time()

    process_directory(INPUT_DIR_PATH)

    # Calculate and display total elapsed time
    elapsed_time = time.time() - stt
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")
