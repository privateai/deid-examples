# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the enabled classes feature.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python enabled_classes.py` or you can define a `.env`
# file which has the line`API_KEY=<your key here>`.

import os
import dotenv
from privateai_client import PAIClient, request_objects

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# On initialization
client = PAIClient("http", "localhost", "8080", api_key=os.environ["API_KEY"])

sample_text = "My name is John and my friend is Grace and we live in Barcelona."
# Create the nested request objects
sample_entity_type_selector = request_objects.entity_type_selector_obj(
    type="ENABLE", value=["NAME", "LOCATION"])
sample_entity_detection = request_objects.entity_detection_obj(
    entity_types=[sample_entity_type_selector])

# Create the request object
process_text_request = request_objects.process_text_obj(
    text=[sample_text], entity_detection=sample_entity_detection)

response = client.process_text(process_text_request)
print(response.processed_text)
