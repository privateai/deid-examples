# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify text.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI< you can run the script as
# `API_KEY=<your key here> python async_call.py` or you can define a `.env` file
# which has the line `API_KEY=<your key here>`.
import os
import pprint
import asyncio
from typing import Dict

import aiohttp
import requests
import dotenv

# Use to load the API key for authentication
dotenv.load_dotenv()

# Define an asynchronous function using the aiohttp library.


async def async_aiohttp_call() -> None:

    # create an asynchronous aiohttp client session
    async with aiohttp.ClientSession() as session:

        # create an asynchronous aiohttp post call
        async with session.post(
            url="http://localhost:8080/deidentify_text",
            json={
                "text": "My name is John and my friend is Grace.",
                "key": os.getenv("API_KEY", "")
            }
        ) as response:

            # print the deidentified text
            pprint.pprint(await response.json())


# Turn synchronous post call from the requests library to an asynchronous call.
async def async_post(
    url: str,
    json: Dict[str, str]
) -> requests.Response:
    return requests.post(
        url=url,
        json=json
    )


async def async_requests_call() -> None:
    response = await async_post(
        url="http://localhost:8080/deidentify_text",
        json={
            "text": "My name is John and my friend is Grace.",
            "key": os.getenv("API_KEY", "")
        }
    )

    # check if the request was successful
    response.raise_for_status()

    # print the result in a readable way
    pprint.pprint(response.json())


if __name__ == "__main__":
    asyncio.run(async_aiohttp_call())
    asyncio.run(async_requests_call())
