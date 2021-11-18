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
        "text": [
            "My password is: 4XDX63F8O1",
            "My password is: 33LMVLLDHNasdfsda"
        ],
        "key": os.getenv("API_KEY", "")
    }
)

# Check if the HTTP request was successful
if response.ok:
    pprint.pprint(response.json())
else:
    raise Exception(
        f"The request failed with status code {response.status_code}"
    )
