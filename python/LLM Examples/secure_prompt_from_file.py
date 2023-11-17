import argparse
import base64
import json
import os
import sys

import demo_config
from openai import OpenAI
from privateai_client import PAIClient, request_objects

# Initialize parser
parser = argparse.ArgumentParser(description="Secure LLM prompting from a file")
parser.add_argument("-d", "--directory", required=True, help="directory")
parser.add_argument("-f", "--file", required=True, help="File to redact")
parser.add_argument("-t", "--filetype", required=True, help="file type")
parser.add_argument("-n", "--filename", required=True, help="file name")
args = parser.parse_args()

PRIVATEAI_API_KEY = demo_config.privateai["PROD_KEY"]
PRIVATEAI_URL = demo_config.privateai["PROD_URL"]

# Initialize the openai client
openai_client = OpenAI(api_key=demo_config.openai["API_KEY"])

file_dir = args.directory
file_name = args.filename
filepath = args.file
file_type = args.filetype.split("/")[1]
PRIVATEAI_SCHEME = "https"
client = PAIClient(PRIVATEAI_SCHEME, PRIVATEAI_URL)
client.add_api_key(PRIVATEAI_API_KEY)


def prompt_chat_gpt(text):
    completion = openai_client.chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": text}]
    )
    return completion.choices[0].message.content


# Read from file
with open(filepath, "rb") as b64_file:
    file_data = base64.b64encode(b64_file.read())
    file_data = file_data.decode("ascii")

# Make the request
file_obj = request_objects.file_obj(data=file_data, content_type=args.filetype)
request_obj = request_objects.file_base64_obj(file=file_obj)
redaction_response = client.process_files_base64(request_object=request_obj)
entity_list = redaction_response.get_reidentify_entities()

# Write to file
with open(os.path.join(file_dir, f"{file_name}.{file_type}"), "wb") as redacted_file:
    processed_file = redaction_response.processed_file.encode("ascii")
    processed_file = base64.b64decode(processed_file, validate=True)
    redacted_file.write(processed_file)

print("\n**************************************************\n")
print(f"redacted file contents: {redaction_response.processed_text}\n")

file_summary = prompt_chat_gpt(
    f"summarize this file: {redaction_response.processed_text}"
)
print("\n SUMMARY \n")
print("********************** redacted summary **********************")
print(file_summary)
print("********************** REID summary **********************")
reid_req_obj = request_objects.reidentify_text_obj(
    processed_text=[file_summary], entities=entity_list
)
reidentification_response_obj = client.reidentify_text(reid_req_obj)
print(reidentification_response_obj.body)
