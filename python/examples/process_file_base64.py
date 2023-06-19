# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the unique PII markers feature (default).
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

file_dir = "/path/to/your/file"
file_name = 'sample_file.pdf'
filepath = os.path.join(file_dir, file_name)
file_type = "type/of_file"  # eg. application/pdf
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
with open(os.path.join(file_dir, f"redacted-{file_name}"), 'wb') as redacted_file:
    processed_file = resp.processed_file.encode("ascii")
    processed_file = base64.b64decode(processed_file, validate=True)
    redacted_file.write(processed_file)
