import time
import asyncio
from os import listdir
from os.path import isfile, join
from helpers.process_file_helpers import submit_job, jobs, get_status, download_file
from dotenv import load_dotenv

INPUT_DIR_PATH = "./data"

async def check_job_status(job_id, file_name):
    return await get_status(job_id, file_name)

async def process_job(job):
    while True:
        if await check_job_status(job.job_id, job.file_name):
            await download_file(job.job_id, job.file_name)
            return
        await asyncio.sleep(5)

async def main():
    load_dotenv()

    # Gather all files in directory
    files = [file for file in listdir(INPUT_DIR_PATH) if isfile(join(INPUT_DIR_PATH, file))]

    # Initialize empty job queue
    job_queue = []

    # Start timer
    stt = time.time()

    # Submit files for processing and add to job queue
    for file_name in files:
        job_id = submit_job(file_name)
        if job_id:
            job_queue.append(jobs(job_id, file_name)) 
    
    tasks = [process_job(job) for job in job_queue]
    await asyncio.gather(*tasks)

    # Calculate and display total elapsed time
    elapsed_time = time.time() - stt
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")

# Run the async event loop
asyncio.run(main())
