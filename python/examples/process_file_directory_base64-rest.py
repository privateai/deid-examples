import os
import dotenv
import requests
import base64
import time
import json 

# Use to load the API KEY for authentication when using the community endpoint
dotenv.load_dotenv()

url = f"http://{os.environ['PRIVATEAI_LOCAL_HOST'] }:8080/"
#url = "https://api.private-ai.com/community/v4/"

headers = {"Content-Type": "application/json", "x-api-key": os.environ["PRIVATEAI_API_KEY"]}

def makePaiCall_file(data, content_type):
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
    ### PRIVATE AI API CALL
    response = requests.post(f"{url}process/files/base64", json=request, headers=headers)
    response.raise_for_status()
    data = response.json()
    ### PRIVATE AI API CALL
    ###----------------------------------------------------------------------------###

    return data

#process file
def pai_redactFile(input_path, mime_type):
    response = None

    print(f"pai_redactFile")
    stt = time.time()
    if os.path.isfile(input_path):
        with open(input_path, "rb") as f:
            file_bytes = f.read()
            b64_str = base64.b64encode(file_bytes).decode("utf-8")
            ct = mime_type

            ###PAI CALL
            response = makePaiCall_file(b64_str,ct)
            ###PAI CALL

    print(f"Done: Total Time {time.time()-stt:.2f}")

    # Extract the 'file: data' element from the response and save the base64 string to a file    
    if response and 'processed_file' in response:
        b64_data = response['processed_file']

        root, ext = os.path.splitext(input_path)
        output_file_path = f"{root}{ext}.redacted{ext}"

        with open(output_file_path, 'wb') as output_file:
            output_file.write(base64.b64decode(b64_data))
        print(f"File saved to {output_file_path}")

        if response and 'processed_file' in response:
            del response['processed_file']

        #write the json
        output_file_path = input_path + '.redacted.json'
        response_content = json.dumps(response, indent=4)
        with open(output_file_path, 'wb') as output_file:                    
            output_file.write(response_content.encode('utf-8'))
        print(f"File saved to {output_file_path}")

    else:
        print("Response does not contain 'file: data'")
    
    return response

#process folder
def pai_redact_folder(folder_path, mime_type_resolver=None, skip_exts=None):
    """Recursively process all files in a folder and subfolders.
    For each file calls `pai_redactFile` and writes outputs as the single-file mode does."""
    results = []
    for root, dirs, files in os.walk(folder_path):
        for name in files:
            input_path = os.path.join(root, name)
            if skip_exts and os.path.splitext(name)[1].lower() in skip_exts:
                print(f"Skipping {input_path}")
                continue
            # Resolve mime type
            mime = None
            if mime_type_resolver:
                try:
                    mime = mime_type_resolver(input_path)
                except Exception as e:
                    print(f"mime_type_resolver error for {input_path}: {e}")
            if not mime:
                ext = os.path.splitext(input_path)[1].lower()
                mapping = {
                    '.pdf': 'application/pdf',
                    '.dcm': 'application/dicom',
                    '.txt': 'text/plain',
                    '.csv': 'text/csv',
                    '.json': 'application/json',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.wav': 'audio/wav',
                    '.mp3': 'audio/mp3',
                    '.m4a': 'audio/m4a'
                }
                mime = mapping.get(ext, 'application/octet-stream')

            print(f"Processing {input_path} (mime={mime})")
            try:
                res = pai_redactFile(input_path, mime)
                results.append({'path': input_path, 'ok': True, 'response': res})
            except Exception as e:
                print(f"Error processing {input_path}: {e}")
                results.append({'path': input_path, 'ok': False, 'error': str(e)})
    return results

# Example usage
file_path = r'C:\MyTestFolder'

pai_redact_folder(file_path)

print("Done")
