# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the fake entity generation feature.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python fake_entity_generation.py` or you can define a
# `.env` file which has the line`API_KEY=<your key here>`.
import os
import dotenv
from privateai_client import PAIClient, request_objects

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# On initialization
client = PAIClient("http", "localhost", "8080", api_key=os.environ["API_KEY"])

process_text_request = {
    "text": [
        'Hello, my name is May. I am the aunt of Pieter Parker. We live in Toronto, Canada.'
    ],
    "link_batch": False,
    "entity_detection": {
        "return_entity": True
    },
    "processed_text": {
        "type": "SYNTHETIC",
        "synthetic_entity_accuracy": "standard",
        "preserve_relationships": True
    }
}

response = client.process_text(process_text_request)
print(response.processed_text)
