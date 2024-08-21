# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a provided file via local file URI.

from privateai_client import PAIClient
from privateai_client.objects import request_objects

input_file = "examples/data/PAI_SYNTH_EN_medical-referral_2.pdf"

client = PAIClient("http", "localhost", "8080")

req_obj = request_objects.file_uri_obj(uri=input_file)
# NOTE this method of file processing requires the container to have an the input and output directories mounted
resp = client.process_files_uri(req_obj)
if resp.ok:
    print(f"File redaction completed: {resp.result_uri}")
else:
    print(f"response for file {input_file} returned with {resp.status_code}")

