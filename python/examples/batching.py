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

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# Check if the API_KEY environment variable is defined
if "API_KEY" not in os.environ:
    raise KeyError("API_KEY must be defined in order to run the examples.")

# Make the POST request to the docker container
response = requests.post(
    url="http://localhost:8080/deidentify_text",
    json={
        "text": [
            "My password is: 4XDX63F8O1",
            "My password is: 33LMVLLDHNasdfsda"
        ],
        "key": os.environ["API_KEY"]
    }
)

# check if the request was successful
response.raise_for_status()

# print the result in a readable way
pprint.pprint(response.json())
