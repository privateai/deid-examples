import os
import pprint

import requests
import dotenv

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# Make the POST request to the docker container
response = requests.post(
    # ! I need the URL of the new demo server.
    url="https://demoprivateai.com",
    json={
        "text": "My name is John and my friend is Grace",
        "key": os.getenv("API_KEY", "")
    }
)

# Check if the HTTP request was successful
if response.ok:
    pprint.pprint(response.json())
else:
    raise Exception(
        f"The request failed with the status code {response.status_code}"
    )
