# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using the non-unique PII markers feature.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python non_unique_pii_markers.py` or you can define a
# `.env` file which has the line`API_KEY=<your key here>`.
import os
import pprint

import requests
import dotenv

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# Make the POST request to the docker container
response = requests.post(
    url="http://localhost:8080/deidentify_text",
    json={
        "text": "My name is John and my friend is Grace",
        "key": os.getenv("API_KEY", ""),
        "unique_pii_markers": False
    }
)

# check if the request was successful
response.raise_for_status()

# print the result in a readable way
pprint.pprint(response.json())
