# Example script to illustrate how to make API calls to the Private AI API
# to deidentify a provided file via base64 encoding.

import time
from helpers.process_file_helpers import submit_job, get_status, download_file

FILE_NAME = "PAI_SYNTH_EN_medical-referral_2.pdf"

# Start timer
stt = time.time()

# Submit file for processing and get job id
job_id = submit_job(FILE_NAME)

# Poll for job completion
while True:
    if get_status(job_id, FILE_NAME):
        break
    time.sleep(5)

# Download deidentified file
download_file(job_id, FILE_NAME)

# Calculate and display total elapsed time
elapsed_time = time.time() - stt
minutes, seconds = divmod(int(elapsed_time), 60)
print(f"Total elapsed time: {minutes} minutes and {seconds} seconds")