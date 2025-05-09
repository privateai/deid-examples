import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in your environment to run the examples.")
if "USER_ID" not in os.environ:
    raise KeyError("USER_ID must be defined in your environment to run the examples.")


PRIVATE_AI_URL = os.getenv("PAI_URL")
USER_ID = os.getenv("USER_ID")


def get_text_request(text_list: list[str]) -> dict:
    return {"text": text_list, "link_batch": True}


def submit_job(text_list: list[str]) -> str:
    request_data = get_text_request(text_list)

    print("Processing text...")

    response = requests.post(f"{PRIVATE_AI_URL}/process/text", json=request_data, headers={"user-id": USER_ID})
    response.raise_for_status()

    # Get the job ID
    job_id = response.json().get("job_id")

    return job_id


def get_state(job_id: str) -> tuple[str, str]:
    session = requests.Session()
    with session.get(f"{PRIVATE_AI_URL}/jobs/{job_id}/state", headers={"user-id": USER_ID}) as response:
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("state"), response_data.get("description")


def get_text(job_id: str) -> list[str]:
    session = requests.Session()
    with session.get(f"{PRIVATE_AI_URL}/jobs/{job_id}", headers={"user-id": USER_ID}) as response:
        response.raise_for_status()
        response_data = response.json()
        return response_data


def process_text(text_array: list[str]) -> tuple[str, str]:
    # Submit text for processing and get job id
    job_id = submit_job(text_array)

    # Poll for job completion
    while True:
        state, description = get_state(job_id)
        if state in ["completed", "downloaded"]:
            print(f"Deidentification finished")
            break
        elif state in ["failed", "expired", "cancelled"]:
            print(f"Deidentification failed with description: {description}")
            return job_id, state
        else:
            print(f"Deidentification state: {state}")
        time.sleep(5)

    # Print deidentified text
    for result in get_text(job_id):
        print(f"processed_text: {result.get('processed_text')}")

    return job_id, state


if __name__ == "__main__":

    # Array of text to be processed
    TEXT_ARRAY = ["Hi my name is michelle", "but you can also call me michhhhh"]

    # Start timer
    stt = time.time()

    # Process the text function
    job_id, state = process_text(TEXT_ARRAY)
    print(f"job_id: {job_id}, state: {state}")

    # Calculate and display total elapsed time
    elapsed_time = time.time() - stt
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")
