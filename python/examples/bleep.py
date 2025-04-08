# This script assumes the input files are: mp3/mp4 for audio and json for transcript
# Transcription schema follows the AWS Transcribe format
# The script looks for sub folders under the ./audio/ folder for processing
# Each subfolder should contain an audio file and the corresponding transcript

import base64
import json
import os
import time

import requests

# Register for a Community API  key at https://private-ai.com
PRIVATE_AI_TEXT_URL = "https://api.private-ai.com/community/v4/process/text"
PRIVATE_AI_BLEEP_URL = "https://api.private-ai.com/community/v4/bleep"
PRIVATE_AI_API_KEY = os.environ["APIKEY"]

# Source directory for input folders
SOURCE_DIRECTORY = "./audio"

# Ouput for audio files
TARGET_DIRECTORY = "./output"

# Response objects for inspection
LOG_DIRECTORY = "./logs"

# Content type dictionary
CONTENT_DICT = {
    ".mp3": "audio/mp3",
    ".mp4": "audio/mp4",
}

# Bleep extra milliseconds before a sensitive word
START_BUFFER = 0.05

# Bleep extra milliseconds after a sensitive word
END_BUFFER = 0.0

# Decible output reduction
BLEEP_GAIN = -20

# Some enabled entities as an example
ENABLED_ENTITIES = [
    "AGE",
    "DATE",
    "DATE_INTERVAL",
    "DOB",
    "EMAIL_ADDRESS",
    "LOCATION",
    "NAME",
    "NAME_MEDICAL_PROFESSIONAL",
    "NUMERICAL_PII",
    "PASSPORT_NUMBER",
    "PHONE_NUMBER",
    "BLOOD_TYPE",
    "CONDITION",
    "DOSE",
    "DRUG",
    "INJURY",
    "MEDICAL_PROCESS",
    "BANK_ACCOUNT",
    "CREDIT_CARD",
    "CREDIT_CARD_EXPIRATION",
    "CVV",
    "ROUTING_NUMBER",
    "EFFECT",
    "MEDICAL_CODE",
]


def log_failure_response(filename: str, response: requests.Response) -> None:
    """Output the response from the service in the case of a failure

    :param filename: The name of the file being worked on
    :param response: The response from the service
    """
    print(f"--- Status: {response.status_code} ---")
    print(f"--- Response: {response.content} ---")
    print(f"--- Reason: {response.reason} ---")

    with open(os.path.join(LOG_DIRECTORY, filename + ".error.txt"), "wt") as response_file:
        response_file.write(f"response.status_code: {response.status_code}\n")
        response_file.write(f"response.headers: {response.headers}\n")
        response_file.write(f"response.url: {response.url}\n")
        response_file.write(f"response.encoding: {response.encoding}\n")
        response_file.write(f"response.text: {response.text}\n")


def get_file_contents(folder: str, files: list[str]) -> dict:
    """Given the list of files, return the contents of the audio and json

    :param folder: The source folder for the files
    :param files: List of file paths
    :return contents: The base64 encoded version of the audio file, filename, and file extension, plus the python version of the transcript
    """

    output = {}

    # Each folder should contain two files, an mp3 and a json
    for file in files:
        filename, ext = os.path.splitext(file)

        if ext in [".mp3", ".mp4"]:
            with open(os.path.join(folder, file), "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
                output["audio"] = {
                    "base64": audio_base64,
                    "filename": filename,
                    "ext": ext,
                }
        elif ext == ".json":
            with open(os.path.join(folder, file), "r") as f:
                transcript_json = json.loads(f.read())
                output["transcript"] = transcript_json

    return output


def get_words_and_timestamps(transcript_json) -> tuple[list[str], list[dict]]:
    """Extract the audio words and each corresponding timestamp from the transcript

    :param transcript_json: The transcript python object containing the words and timestamps
    :return text, timestamps: The transcript words and punctuation, plus the corresponding timestamps
    """
    text = []
    timestamps = []

    for item in transcript_json["results"]["items"]:
        # Keep track of all text to send to the de-identification service
        text.append(item["alternatives"][0]["content"])

        # Punctuation added by the transcription service doesn't include timestamps, but we must include something so the arrays are the same size
        if item["type"] == "pronunciation":
            timestamps.append(
                {"start": float(item["start_time"]) - START_BUFFER, "end": float(item["end_time"]) + END_BUFFER}
            )
        else:
            timestamps.append({})

    return text, timestamps


if __name__ == "__main__":

    session = requests.Session()

    headers = {"x-api-key": PRIVATE_AI_API_KEY}

    # Search through each subdirectory
    for folder, subdirs, files in os.walk(SOURCE_DIRECTORY):

        # Skip the root audio directory
        if not files:
            continue

        print(f"--- Attempting to process {folder} at {time.ctime()} ---")

        file_contents = get_file_contents(folder, files)

        text, timestamps = get_words_and_timestamps(transcript_json=file_contents["transcript"])

        request_text = {
            "text": text,
            "link_batch": True,
            "entity_detection": {
                "entity_types": [
                    {
                        "type": "ENABLE",
                        "value": ENABLED_ENTITIES,
                    },
                ],
            },
        }

        try:
            text_stt = time.time()

            # Send text transcript to de-identification service
            with session.post(url=PRIVATE_AI_TEXT_URL, headers=headers, json=request_text) as text_response:
                print(f"--- Text completed: {time.time() - text_stt} seconds at {time.ctime()} ---")

                if text_response.ok:
                    text_response_json = text_response.json()

                    bleep_timestamps = []

                    # For any entities found, keep track of the timestamps for the detected word
                    for entity, timestamp in zip(text_response_json, timestamps):
                        if entity["entities_present"]:
                            bleep_timestamps.append(timestamp)

                    # Write text output to file for reference
                    with open(
                        os.path.join(LOG_DIRECTORY, file_contents["audio"]["filename"] + ".text_response.json"), "wt"
                    ) as response_file:
                        response_file.write(json.dumps(text_response_json))

                    request_bleep = {
                        "file": {
                            "data": file_contents["audio"]["base64"],
                            "content_type": CONTENT_DICT[file_contents["audio"]["ext"]],
                        },
                        "timestamps": bleep_timestamps,
                        "bleep_gain": BLEEP_GAIN,
                    }

                    bleep_stt = time.time()

                    # Send audio file with timestamps for bleeping
                    with session.post(url=PRIVATE_AI_BLEEP_URL, headers=headers, json=request_bleep) as bleep_response:
                        print(f"--- File completed: {time.time() - bleep_stt} seconds at {time.ctime()} ---")
                        if bleep_response.ok:
                            with open(
                                os.path.join(
                                    TARGET_DIRECTORY,
                                    file_contents["audio"]["filename"] + ".redacted" + file_contents["audio"]["ext"],
                                ),
                                "wb",
                            ) as redacted_file:
                                redacted_file.write(base64.b64decode(bleep_response.json()["bleeped_file"]))

                        else:
                            log_failure_response(filename=file_contents["audio"]["filename"], response=bleep_response)

                else:
                    log_failure_response(filename=file_contents["audio"]["filename"], response=text_response)

        except Exception as e:
            print(f"Exception occurred: {e}")
            print(f"--- Elapsed time: {time.time() - text_stt} seconds ---")
