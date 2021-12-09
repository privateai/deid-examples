# Example script to illustrate how to make API calls to the Private AI Docker
# container to deidentify a text using concurrency.
#
# To use this script, please start the Docker container locally, as per the
# instructions at https://private-ai.com/docs/installation.
#
# In order to use the API key issued by Private AI, you can run the script as
# `API_KEY=<your key here> python concurrency.py` or you can define a `.env`
# file which has the line`API_KEY=<your key here>`.
import os
import pprint

# For this example, only the threading and the concurrent.futures libraries are
# used to keep the examples concise. Since the multiprocessing.Process class has
# the same API as the threading.Thread class, you can follow the threading
# examples to implement concurrency using the multiprocessing library.
import threading
import concurrent.futures
from typing import Dict, List

import requests
import dotenv

# define the function that will make the POST request and print the result
def make_request(url: str, json: Dict[str, str]) -> Dict[str, str]:
    response = requests.post(url=url, json=json)

    # check if the request was successful
    response.raise_for_status()

    # return the body of the response
    return response.json()


# function that pretty prints the response
def print_result(url: str, json: Dict[str, str]) -> None:
    response = make_request(url, json)
    pprint.pprint(response)


# function that accepts a variable that will hold the result of the make_request
# function
def return_make_request(
    url: str,
    json: Dict[str, str],
    response: List[Dict[str, str]]
) -> None:
    response.append(make_request(url, json))


# Concurrency example using the threading library
def threading_example() -> None:

    # initialize the Thread object
    requests_thread = threading.Thread(
        target=print_result,
        kwargs={
            "url": "http://localhost:8080/deidentify_text",
            "json": {
                "text": "My name is John and my friend is Grace.",
                "key": os.environ["API_KEY"]
            }
        }
    )

    # start the tread
    requests_thread.start()

    # use the following line to block the main thread until the requests_thread
    # terminates
    requests_thread.join()


# Concurrency example using the threading library, get the return from the
# terminated thread to the main thread
def threading_example_with_return() -> None:

    # initialize the variable that will hold the result from the thread
    response = []

    # initialize the Thread object
    thread = threading.Thread(
        target=return_make_request,
        kwargs={
            "url": "http://localhost:8080/deidentify_text",
            "json": {
                "text": "My name is John and my friend is Grace.",
                "key": os.environ["API_KEY"]
            },
            "response": response
        }
    )

    # start the thread
    thread.start()

    # block the main thread until the thread terminates
    thread.join()

    # print the result
    pprint.pprint(response)


# Concurrency example using the Thread Pool from the concurrent.futures library
def concurrent_thread_pool_example() -> None:

    # instantiate the thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = [executor.submit(
            make_request,
            url="http://localhost:8080/deidentify_text",
            json={
                "text": "My name is John and my friend is Grace.",
                "key": os.environ["API_KEY"]
            }
        )]

        for completed in concurrent.futures.as_completed(future):
            pprint.pprint(completed.result())


# Concurrency example using the Process Poll from the concurrent.futures library
def concurrent_process_pool_example() -> None:

    # instantiate the process pool
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = [executor.submit(
            print_result,
            url="http://localhost:8080/deidentify_text",
            json={
                "text": "My name is John and my friend is Grace.",
                "key": os.environ["API_KEY"]
            }
        )]

        # wait for the process to be complete
        concurrent.futures.wait(future)


if __name__ == "__main__":
    
    # Use to load API KEY for authentication
    dotenv.load_dotenv()

    # Check if API_KEY environment variable is defined
    if "API_KEY" not in os.environ:
        raise KeyError("API_KEY must be defined in order to run the examples.")

    print("\nConcurrency example using the threading library:")
    threading_example()
    print(
        "\nConcurrency example using the threading library, access return result from the thread:"
    )
    threading_example_with_return()
    print(
        "\nConcurrency example using the ThreadPoolExecutor class from the concurrent.futures library:"
    )
    concurrent_thread_pool_example()
    print(
        "\nConcurrency example using the ProcessPoolExecutor class from the concurrent.futures library:"
    )
    concurrent_process_pool_example()
