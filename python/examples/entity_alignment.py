import requests
import json
import os
import dotenv
import re
from collections import defaultdict, deque

dotenv.load_dotenv()

#url = "http://localhost:8080/"
url = "https://api.private-ai.com/community/v4/"
headers = {"Content-Type": "application/json", "x-api-key": os.environ["PRIVATEAI_API_KEY"]}

#Simple example that demonstrates the entity alignment concept utilized within the Limina platform product
#This code sample looks at the detected PII and entity markers, and ensures that markers are aligned upon subsequent calls
#This code requires that each response be retained in memory and does not retain state.

def align_processed_text(response1, response2):
    """Update response2 entities with processed_text values from matching response1 entities."""
    processed_text_by_value = defaultdict(deque)
    highest_number_by_prefix = defaultdict(int)
    used_processed_text = set()
    marker_pattern = re.compile(r"^(?P<prefix>.+)_(?P<number>\d+)$")

    for response in response1:
        for entity in response.get("entities", []):
            processed_text = entity["processed_text"]
            processed_text_by_value[entity["text"]].append(processed_text)
            used_processed_text.add(processed_text)
            marker_match = marker_pattern.match(processed_text)
            if marker_match:
                prefix = marker_match.group("prefix")
                highest_number_by_prefix[prefix] = max(
                    highest_number_by_prefix[prefix], int(marker_match.group("number"))
                )

    for response in response2:
        marker_updates = []
        for entity in response.get("entities", []):
            original_processed_text = entity.get("processed_text")
            matching_processed_text = processed_text_by_value.get(entity.get("text"))
            if matching_processed_text:
                entity["processed_text"] = matching_processed_text.popleft()
            else:
                processed_text = entity.get("processed_text")
                marker_match = marker_pattern.match(processed_text or "")
                if marker_match and processed_text in used_processed_text:
                    prefix = marker_match.group("prefix")
                    highest_number_by_prefix[prefix] += 1
                    entity["processed_text"] = (
                        f"{prefix}_{highest_number_by_prefix[prefix]}"
                    )
                used_processed_text.add(entity.get("processed_text"))
            location = entity.get("location", {})
            if (
                isinstance(response.get("processed_text"), str)
                and isinstance(location.get("stt_idx_processed"), int)
                and isinstance(location.get("end_idx_processed"), int)
                and original_processed_text != entity.get("processed_text")
            ):
                marker_updates.append(
                    (
                        location["stt_idx_processed"],
                        location["end_idx_processed"],
                        entity["processed_text"],
                        location,
                    )
                )

        for start, end, processed_text, location in sorted(
            marker_updates, reverse=True
        ):
            response["processed_text"] = (
                response["processed_text"][:start]
                + f"[{processed_text}]"
                + response["processed_text"][end:]
            )
            location["end_idx_processed"] = start + len(processed_text) + 2

    return response2



def makePaiCall_text(data):
    request = {
        "text": data,
        "link_batch":True        
    }
    
    ###----------------------------------------------------------------------------###
    ### PRIVATE AI API CALL
    response = requests.post(f"{url}process/text", json=request, headers=headers)
    response.raise_for_status()
    data = response.json()
    ### PRIVATE AI API CALL
    ###----------------------------------------------------------------------------###

    return data


input_text = ["Hi Aaron its Jeff",
              "Hi jeff its nice to meet you"]

input_text2 = ["Susan held a meeting with Jeff and Aaron"]


response1 = makePaiCall_text(input_text)

response2 = makePaiCall_text(input_text2)
response2 = align_processed_text(response1, response2)

#TODO: To ensure no drift occurs across markers, all responses will need to be aggregated and continuously concatenated

#Print output
formatted_str = json.dumps(response1, indent=4)
print(formatted_str)

formatted_str = json.dumps(response2, indent=4)
print(formatted_str)