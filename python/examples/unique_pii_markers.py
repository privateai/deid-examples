import os
import pprint

import requests
import dotenv

# Use to load the API KEY for authentication
dotenv.load_dotenv()
BASE_URL = "http://localhost:8080"

# Make the POST request to the container
response = requests.post(
    url=f"{BASE_URL}/deidentify_text",
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
        f"There was an error with the request. Status Code {response.status_code}"
    )
