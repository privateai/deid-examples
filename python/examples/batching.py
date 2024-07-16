# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the batching feature.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python batching.py` or you can define a `.env` file
# which has the line`API_KEY=<your key here>`.

import os
import dotenv
from privateai_client import PAIClient, request_objects

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# On initialization
client = PAIClient("http", "localhost", "8080", api_key=os.environ["API_KEY"])

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
