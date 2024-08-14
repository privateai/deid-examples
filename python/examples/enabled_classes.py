# Example script to illustrate how to make API calls to the Private AI API
# to deidentify text using the enabled classes feature.

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
