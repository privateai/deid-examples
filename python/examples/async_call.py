# Example script to illustrate how to make API calls to the Private AI API
# to deidentify text.

import aiohttp
import asyncio
import dotenv
import requests
import os
import pprint

dotenv.load_dotenv()

# Our other deid_example files use the privateai_client, but these do not just to simply demonstrate async calls with async built libraries

# Define an asynchronous function using the aiohttp library.
async def async_aiohttp_call() -> None:

    # create an asynchronous aiohttp client session
    async with aiohttp.ClientSession() as session:

        # create an asynchronous aiohttp post call, done outside the private ai client to use aiohttp
        async with session.post(
            url=f"{os.environ["PAI_URL"]}/v3/process/text",
            json={
                "text": ["My name is John and my friend is Grace."],
            },
            headers={"x-api-key": os.environ["API_KEY"]}
        ) as response:

            # print the deidentified text
            pprint.pprint(await response.json())


# Turn synchronous post call from the requests library to an asynchronous call.
async def async_post(
    url: str,
    json: dict[str, str],
    headers: dict[str, str]
) -> requests.Response:
    return requests.post(
        url=url,
        json=json,
        headers=headers
    )


async def async_requests_call() -> None:
    response = await async_post(
        url=f"{os.environ["PAI_URL"]}/v3/process/text",
        json={
            "text": ["My name is John and my friend is Grace."]
        },
        headers={"x-api-key": os.environ["API_KEY"]}
    )

    # check if the request was successful
    response.raise_for_status()

    # print the result in a readable way
    pprint.pprint(response.json())


if __name__ == "__main__":
    
    # Use to load the API key and URL
    dotenv.load_dotenv()
    
    # Check if the API_KEY and PAI_URL environment variables are set
    if "API_KEY" not in os.environ:
        raise KeyError("API_KEY must be defined in .env to run the examples.")
    if "PAI_URL" not in os.environ:
        raise KeyError("PAI_URL must be defined in .env to run the examples.")

    # Run the examples
    asyncio.run(async_aiohttp_call())
    asyncio.run(async_requests_call())
