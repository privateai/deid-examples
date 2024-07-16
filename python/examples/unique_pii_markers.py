# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the unique PII markers feature (default).
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python unique_pii_markers.py` or you can define a
# `.env` file which has the line`API_KEY=<your key here>`.

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
    text=["My name is John and my friend is Grace and we live in Barcelona",],
    link_batch=False,
    entity_detection=entity_detection_obj,
    processed_text=processed_text_obj
)

response = client.process_text(process_text_request)
print(response.processed_text)
