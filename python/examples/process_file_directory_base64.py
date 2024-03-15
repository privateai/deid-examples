# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify all files in a provided directory.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python process_file_base64.py` or you can define a
# `.env` file which has the line`API_KEY=<your key here>`.

from privateai_client import PAIClient
from privateai_client.objects import request_objects

import base64
import os
import logging

from os import listdir
from os.path import isfile, join

dir_path = "/path/to/directory"

# Supported file types as of March 2024
file_type_dict = {
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
files = [file for file in listdir(dir_path) if isfile(join(dir_path, file))]

for file_name in files:
    
    file_ext = file_name[file_name.rfind("."):] # Gets the file extension
    if file_ext in file_type_dict:
        filepath = os.path.join(dir_path, file_name)
        file_type = file_type_dict[file_ext]
        client = PAIClient("http", "localhost", "8080")

        # Read from file
        with open(filepath, "rb") as b64_file:
            file_data = base64.b64encode(b64_file.read())
            file_data = file_data.decode("ascii")

        # Make the request
        file_obj = request_objects.file_obj(data=file_data, content_type=file_type)
        request_obj = request_objects.file_base64_obj(file=file_obj)
        resp = client.process_files_base64(request_object=request_obj)
        if not resp.ok:
            logging.error(
                f"response for file {file_name} returned with {resp.status_code}")

        # Write to file
        with open(os.path.join(dir_path, f"redacted-{file_name}"), 'wb') as redacted_file:
            processed_file = resp.processed_file.encode("ascii")
            processed_file = base64.b64decode(processed_file, validate=True)
            redacted_file.write(processed_file)
    else:
        print(f"File {file_name} not supported and will not be redacted.")
