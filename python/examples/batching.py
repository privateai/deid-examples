# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a text using the batching feature.

import dotenv
import os
from privateai_client import PAIClient, request_objects

# Use to load the API KEY and URL
dotenv.load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "API_KEY" not in os.environ:
    raise KeyError("API_KEY must be defined in .env to run the examples.")
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in .env to run the examples.")

# Client initialization
client = PAIClient(url=os.environ["PAI_URL"], api_key=os.environ["API_KEY"])

entity_detection_obj = request_objects.entity_detection_obj(return_entity=True)

processed_text_obj = request_objects.processed_text_obj(type="MARKER")

process_text_request = request_objects.process_text_obj(
    text=["Hi, my name is Penelope, could you tell me your phone number please?",
          "Sure, x234",
          "and your DOB please?",
          "fourth of Feb nineteen 86"],
    link_batch=True,
    entity_detection=entity_detection_obj,
    processed_text=processed_text_obj
)

response = client.process_text(process_text_request)
print(response.processed_text)
