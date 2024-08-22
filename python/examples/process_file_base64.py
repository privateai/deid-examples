# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a provided file via base64 encoding.


import base64
import dotenv
import os

from privateai_client import PAIClient, request_objects

input_file_dir = "examples/data"
output_file_dir = "examples/output"
file_name = "PAI_SYNTH_EN_medical-referral_2.pdf"
filepath = os.path.join(input_file_dir, file_name)
file_type = "application/pdf"

# Use to load the API KEY and URL
dotenv.load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "API_KEY" not in os.environ:
    raise KeyError("API_KEY must be defined in .env to run the examples.")
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in .env to run the examples.")

# Client initialization
client = PAIClient(url=os.environ["PAI_URL"], api_key=os.environ["API_KEY"])

# Read from file
with open(filepath, "rb") as b64_file:
    file_data = base64.b64encode(b64_file.read())
    file_data = file_data.decode()

# Make the request
file_obj = request_objects.file_obj(data=file_data, content_type=file_type)
request_obj = request_objects.file_base64_obj(file=file_obj)
resp = client.process_files_base64(request_object=request_obj)

if not resp.ok:
    print(f"response for file {file_name} returned with {resp.status_code}")

# Write to file
with open(os.path.join(output_file_dir, f"redacted-{file_name}"), 'wb') as redacted_file:
    processed_file = resp.processed_file
    processed_file = base64.b64decode(processed_file, validate=True)
    redacted_file.write(processed_file)
    print(f"File redaction completed: {redacted_file.name}")
