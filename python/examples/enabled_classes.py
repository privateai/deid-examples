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
