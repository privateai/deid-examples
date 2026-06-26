import os
import subprocess
import tempfile
import shutil
import glob
import requests
import base64
import time
import concurrent.futures
import json

url = f"http://localhost:8080/"

headers = {"Content-Type": "application/json"}

def makeLiminaiCall_file(data, content_type):
    #Issue single base64 call
    request = {
        "file": { 
            "data": data,
            "content_type": content_type        
        },
        #Example with multiple entities enabled
        "entity_detection": {
            "entity_types": [
            {
                "type": "ENABLE",
                "value": ["EMAIL_ADDRESS","LOCATION","LOCATION_ADDRESS","LOCATION_ADDRESS_STREET","LOCATION_CITY","LOCATION_COUNTRY","LOCATION_STATE","LOCATION_ZIP","NAME","NAME_FAMILY","NAME_GIVEN","PHONE_NUMBER","BANK_ACCOUNT","CREDIT_CARD","CREDIT_CARD_EXPIRATION","CVV","ROUTING_NUMBER"]
            }
            ]
        }
    }
    
    ###----------------------------------------------------------------------------###
    ### LIMINA CALL
    response = requests.post(f"{url}process/files/base64", json=request, headers=headers, timeout=(10, 60))
    response.raise_for_status()
    result = response.json()    
    ### LIMINA CALL
    ###----------------------------------------------------------------------------###

    return result

#process file
def limina_redactFile(input_path, mime_type) -> str:
    output_file_path = ""

    if os.path.isfile(input_path):
        #Read input file into base64 string
        with open(input_path, "rb") as f:
            file_bytes = f.read()
            b64_str = base64.b64encode(file_bytes).decode("utf-8")
            ct = mime_type

        ###LIMINA CALL
        response = makeLiminaiCall_file(b64_str,ct)        
        ###LIMINA CALL

        # Extract the 'file: data' element from the response and save the base64 string to a file
        if response and 'processed_file' in response:
            b64_data = response['processed_file']

            root, ext = os.path.splitext(input_path)
            output_file_path = f"{root}{ext}.redacted{ext}"

            with open(output_file_path, 'wb') as output_file:
                output_file.write(base64.b64decode(b64_data))
            #print(f"File saved to {output_file_path}", flush=True)

        else:
            print("Response does not contain 'file: data'", flush=True)
    
    return output_file_path

#split frames
def split_frames(input_path: str, frames_dir: str):
    print("Extracting frames...")
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, os.path.join(frames_dir, "frame_%06d.png")],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )

    frame_paths = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    print(f"  {len(frame_paths)} frames extracted")

    return frame_paths

def redact_frame(frame_path: str, redacted_dir: str):
    max_attempts = 4
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            #Main file redaction call            
            redacted_src = limina_redactFile(frame_path, "image/png")

            #Move the redacted file to the output dir
            if os.path.isfile(redacted_src):
                dest = os.path.join(redacted_dir, os.path.basename(frame_path))
                shutil.move(redacted_src, dest)
                return
            raise RuntimeError(f"Redacted frame not produced for {frame_path}")
        except Exception as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            wait = 2 ** (attempt - 1)
            print(f"  redact_frame - Retry {attempt}/{max_attempts} for {frame_path} after error: {exc}", flush=True)
            time.sleep(wait)
    raise last_error

def redact_frames(frame_paths, redacted_dir: str):
    total = len(frame_paths)
    print(f"Redacting frames... ({total} total)")

    outstanding = {os.path.basename(p) for p in frame_paths}
    done = 0

    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        future_to_frame = {
            executor.submit(redact_frame, fp, redacted_dir): os.path.basename(fp)
            for fp in frame_paths
        }
        failures = []
        for future in concurrent.futures.as_completed(future_to_frame):
            frame_name = future_to_frame[future]
            outstanding.discard(frame_name)
            done += 1

            try:
                future.result()
            except Exception as e:
                failures.append((frame_name, e))
                print(f"  ERROR: {frame_name} failed: {e}", flush=True)

            if outstanding:
                sorted_outstanding = sorted(outstanding)
                display = sorted_outstanding[:5]
                suffix = f" (+{len(sorted_outstanding) - 5} more)" if len(sorted_outstanding) > 5 else ""
                print(f"  Progress: {done}/{total} done - Outstanding: {', '.join(display)}{suffix}", flush=True)
            else:
                print(f"  Progress: {done}/{total} done", flush=True)

    if failures:
        names = ", ".join(f for f, _ in failures)
        raise RuntimeError(f"{len(failures)} frame(s) failed: {names}")

def redact_audio_file(work_dir: str, input_path: str):    
    print("Extracting audio track...")
    audio_file = os.path.join(work_dir, "audio.m4a")
    extract_cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn",  # no video
        "-acodec", "aac",
        audio_file
    ]
    result = subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    
    if os.path.isfile(audio_file) and os.path.getsize(audio_file) > 0:
        print("Redacting audio track...")
        try:
            limina_redactFile(audio_file, "audio/m4a")
        except Exception as exc:
            print(f"Warning: Audio redaction failed after retries: {exc}. Using original audio", flush=True)
            return input_path
        
        redacted_audio = audio_file + ".redacted.m4a"
        if os.path.isfile(redacted_audio):
            audio_input_path = redacted_audio
            print(f"Audio redacted and saved")
        else:
            print("Warning: Audio redaction did not produce output, using original audio", flush=True)
            audio_input_path = input_path
    else:
        print("Warning: No audio track found in video, skipping audio redaction")
        audio_input_path = input_path

    return audio_input_path


def reassemble_file(input_path: str,redacted_dir: str,audio_input_path: str, output_path:str ):
    probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1",
             input_path],
            check=True, capture_output=True, text=True
        )
    fps_str = probe.stdout.strip()  # e.g. "30/1" or "2997/100"
    num, den = fps_str.split("/")
    fps = float(num) / float(den)
    print(f"  Source frame rate: {fps:.4f} fps")

    # --- 5. Reassemble redacted frames + audio ---
    print("Reassembling video...")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(redacted_dir, "frame_%06d.png"),
            "-i", audio_input_path,
            "-map", "0:v:0", "-map", "1:a?",   # video from frames, audio from (original or redacted)
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            output_path
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    print(f"Redacted video saved to {output_path}")

    return output_path


def limina_redact_video(input_path, output_path=None, redact_audio=True):
    """Extract every frame from a video with FFmpeg, redact each frame via Limina,
    then reassemble the redacted frames (plus original or redacted audio) into a new video file.

    Args:
        input_path (str): Path to the input video file
        output_path (str, optional): Path for the output video. If None, creates output next to input with .redacted suffix
        redact_audio (bool, optional): If True, extract, redact, and reintegrate audio track. Default is True.
    """

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input video not found: {input_path}")

    if output_path is None:
        root, ext = os.path.splitext(input_path)
        output_path = f"{root}.redacted{ext}"

    work_dir = tempfile.mkdtemp(prefix="limina_video_")
    try:
        frames_dir = os.path.join(work_dir, "frames")
        redacted_dir = os.path.join(work_dir, "redacted")
        os.makedirs(frames_dir)
        os.makedirs(redacted_dir)

        # --- 1. Extract frames ---
        frame_paths = split_frames(input_path, frames_dir)

        # --- 2. Redact each frame ---
        redact_frames(frame_paths, redacted_dir)

        # --- 3. Extract and redact audio (if requested) ---
        audio_input_path = input_path
        if redact_audio:
            audio_input_path = redact_audio_file(work_dir, input_path)

        # --- 4. Rebuild file ---
        output_path = reassemble_file(input_path,redacted_dir,audio_input_path, output_path)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return output_path


limina_redact_video(r"C:\Users\AaronYemm\Pictures\Camera Roll\WIN_20260625_15_16_09_Pro.mp4")

print("Done")
