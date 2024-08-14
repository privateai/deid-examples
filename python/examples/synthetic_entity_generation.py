# Example script to illustrate how to make API calls to the Private AI API
# to deidentify text using the synthetic entity generation feature.

import dotenv
import os
from privateai_client import PAIClient, request_objects

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "API_KEY" not in os.environ:
    raise KeyError("API_KEY must be defined in .env to run the examples.")
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in .env to run the examples.")

# Client initialization
client = PAIClient(url=os.environ["PAI_URL"], api_key=os.environ["API_KEY"])

sample_text = "Hello, my name is May. I am the aunt of Pieter Parker. We live in Toronto, Canada."
sample_entity_detection = request_objects.entity_detection_obj(return_entity=True)
sample_processed_text = request_objects.processed_text_obj(
    type="SYNTHETIC",
    synthetic_entity_accuracy="standard",
    preserve_relationships=True
)
process_text_request = request_objects.process_text_obj(
   text=[sample_text],
   link_batch=False,
   entity_detection=sample_entity_detection,
   processed_text=sample_processed_text
)

response = client.process_text(process_text_request)
print(response.processed_text)
