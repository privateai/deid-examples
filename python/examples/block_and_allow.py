# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a text using the enabled classes feature.

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


# Here is the same text we are going to analyze. In this example we will block Names, Locations, and Cities.
# We will also create a custom block list to demonstration how to block custom strings that aren't part of 
# our default entities. We will also create an allow list to show how to allow things like specific cities 
# to pass through redaction, while catching all other cities.

sample_text = "My name is John and my friend is Grace and we live in Barcelona, not Toronto. I SHOULD BLOCK THIS"

# Create the nested request objects
sample_entity_type_selector = request_objects.entity_type_selector_obj(
    type="ENABLE", value=["NAME", "LOCATION","LOCATION_CITY"])

# This is a block filter where you can define strings or regex patterns to block
block_string = request_objects.filter_selector_obj(
    type="BLOCK", entity_type="CUSTOM_ENTITY", pattern="I SHOULD BLOCK THIS"
)

# Similarily, this is an allow list. In this case I want to always allow Barcelona to pass 
# but no other location
allow_string = request_objects.filter_selector_obj(
    type="ALLOW", pattern="Barcelona"
)

sample_entity_detection = request_objects.entity_detection_obj(
    entity_types=[sample_entity_type_selector],
    filter=[block_string,allow_string]
    )

# Create the request object
process_text_request = request_objects.process_text_obj(
    text=[sample_text],
    entity_detection=sample_entity_detection,
    )

response = client.process_text(process_text_request)
print(response.processed_text)
