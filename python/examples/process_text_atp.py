import asyncio
import time
from helpers.process_text_helpers import submit_job, get_status, return_text

LINK_BATCH = False

async def process_text():
    # Start timer
    stt = time.time()

    # Array of text to be processed
    text_array = [
        "Hi my name is michelle", "but you can also call me michhhhh"
    ]

    # Submit text for processing and get job id
    job_id = submit_job(text_array, LINK_BATCH)

    # Poll for job completion
    while True:
        if await get_status(job_id):
            break
        await asyncio.sleep(5)

    # Print deidentified text
    await return_text(job_id)

    # Calculate and display total elapsed time
    elapsed_time = time.time() - stt
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")

# Run the async function
asyncio.run(process_text())
