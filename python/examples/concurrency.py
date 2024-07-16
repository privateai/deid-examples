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
import logging
import pprint

# For this example, only the threading and the concurrent.futures libraries are
# used to keep the examples concise. Since the multiprocessing.Process class has
# the same API as the threading.Thread class, you can follow the threading
# examples to implement concurrency using the multiprocessing library.
import threading
import concurrent.futures
from typing import Dict, List

import dotenv

from privateai_client import PAIClient, request_objects

# Use to load the API KEY for authentication
dotenv.load_dotenv()

# On initialization
client = PAIClient("http", "localhost", "8080", api_key=os.environ["API_KEY"])

# define the function that will make the POST request and print the result
def make_request(request: request_objects.process_text_obj) -> Dict[str, str]:
    
    response = client.process_text(request)

    # check if the request was successful
    if response.ok: 
        # return the response
        return response.processed_text
    else:
        logging.error(f"response returned with error code: {response.status_code}")


# function that pretty prints the response
def print_result(request: request_objects.process_text_obj) -> None:
    response = make_request(request)
    pprint.pprint(response)


# function that accepts a variable that will hold the result of the make_request
# function
def return_make_request(
    request: request_objects.process_text_obj, response: List) -> None:
    response.append(make_request(request))


# Concurrency example using the threading library
def threading_example() -> None:

    entity_detection_obj = request_objects.entity_detection_obj(return_entity=True)

    processed_text_obj = request_objects.processed_text_obj(type="MARKER")

    process_text_request = request_objects.process_text_obj(
        text=["Hi, my name is Penelope, could you tell me your phone number please?",
            "Sure, x234",
            "and your DOB please?",
            "fourth of Feb nineteen 86"],
        link_batch=True,
        entity_detection=entity_detection_obj,
        processed_text=processed_text_obj
    )

    # initialize the Thread object
    requests_thread = threading.Thread(
        target=print_result,
        kwargs={
            "request": process_text_request
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

    entity_detection_obj = request_objects.entity_detection_obj(return_entity=True)

    processed_text_obj = request_objects.processed_text_obj(type="MARKER")

    process_text_request = request_objects.process_text_obj(
        text=["Hi, my name is Penelope, could you tell me your phone number please?",
            "Sure, x234",
            "and your DOB please?",
            "fourth of Feb nineteen 86"],
        link_batch=True,
        entity_detection=entity_detection_obj,
        processed_text=processed_text_obj
    )
    
    # initialize the Thread object
    thread = threading.Thread(
        target=return_make_request,
        kwargs={
            "request": process_text_request,
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

    entity_detection_obj = request_objects.entity_detection_obj(return_entity=True)

    processed_text_obj = request_objects.processed_text_obj(type="MARKER")

    process_text_request = request_objects.process_text_obj(
        text=["Hi, my name is Penelope, could you tell me your phone number please?",
            "Sure, x234",
            "and your DOB please?",
            "fourth of Feb nineteen 86"],
        link_batch=True,
        entity_detection=entity_detection_obj,
        processed_text=processed_text_obj
    )
    
    # instantiate the thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = [executor.submit(
            make_request,
            request=process_text_request
        )]

        for completed in concurrent.futures.as_completed(future):
            pprint.pprint(completed.result())


# Concurrency example using the Process Poll from the concurrent.futures library
def concurrent_process_pool_example() -> None:

    entity_detection_obj = request_objects.entity_detection_obj(return_entity=True)
    
    processed_text_obj = request_objects.processed_text_obj(type="MARKER")

    process_text_request = request_objects.process_text_obj(
        text=["Hi, my name is Penelope, could you tell me your phone number please?",
            "Sure, x234",
            "and your DOB please?",
            "fourth of Feb nineteen 86"],
        link_batch=True,
        entity_detection=entity_detection_obj,
        processed_text=processed_text_obj
    )
    
    # instantiate the process pool
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = [executor.submit(
            print_result,
            request=process_text_request
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