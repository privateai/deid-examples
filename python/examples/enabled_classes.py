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
import pprint

import requests
import dotenv

# Use to load API KEY for authentication
dotenv.load_dotenv()

# Make the POST request to the docker container
response = requests.post(
    url="http://localhost:8080/deidentify_text",
    json={
        "text": "My name is John and my friend is Grace and we live in Barcelona",
        "key": os.getenv("API_KEY", ""),
        "enabled_classes": ["AGE", "LOCATION"]
    }
)

# Check if the HTTP request was successful
if response.ok:
    pprint.pprint(response.json())
else:
    raise Exception(
        f"The request failed with the status code {response.status_code}"
    )
