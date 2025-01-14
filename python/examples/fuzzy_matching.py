# Example script to illustrate how to make calls to the Private AI API to
# deidentify text and match the detected entites against a list of words.
# Replace the detected entities if the distance is less than a certain
# threshold.

import dotenv
from itertools import groupby
import os

from pyxdameraulevenshtein import damerau_levenshtein_distance
from privateai_client import PAIClient, request_objects

# Use to load the API KEY and URL
dotenv.load_dotenv()

# Check if the API_KEY and PAI_URL environment variables are set
if "API_KEY" not in os.environ:
    raise KeyError("API_KEY must be defined in .env to run the examples.")
if "PAI_URL" not in os.environ:
    raise KeyError("PAI_URL must be defined in .env to run the examples.")

# Client initialization
client = PAIClient(url=os.environ["PAI_URL"], api_key=os.environ["API_KEY"])


class NotComparable(str):
        """Turns a string (_e.g._, a string literal like "e") which would otherwise compare equal to itself non-comparable"""
        def __init__(self, value: str):
            self.value = value

samples = [
    {
        "text": "My name is John and my friend is Grace and we live in Barcelonnaa, not Torotno. I would like to move to Madrid.",
        "words": ["Barcelona", "Toronto"]
    },
    {
        "text": "A 40-year-old femael with a history of type 2 diabetes and hypertenssion presented with an enlarged spleen and persistent fatigue. Further testing indicated Gaucher disease, explaining her frequent joint pain and low platelet count.",
        "words": ["female", "Hypertension"]
    }
]

sample_entity_detection = request_objects.entity_detection_obj(return_entity=True)

for sample in samples:
    text, words = sample["text"], sample["words"]

    process_text_request = request_objects.ner_text_obj(
        text=[text],
        entity_detection=sample_entity_detection
    )

    response = client.ner_text(process_text_request)

    entities = response.entities[0]

    threshold = 2
    for entity in entities:
        # calculate Damereu Lenvenshtien distance between detected entities and each word
        distances = [damerau_levenshtein_distance(entity["text"], word) for word in words]

        # get the index of the word with the minimum distance
        min_dist_idx = distances.index(min(distances))

        # replace the detected entity with the word with the minimum distance if the distance is less than the threshold
        entity["text"] = words[min_dist_idx] if min(distances) <= threshold else entity["text"]

    redacted_chunks = [NotComparable(c) for c in text]

    for entity in entities:
        start = entity["location"]["stt_idx"]
        end = entity["location"]["end_idx"]
        redacted_chunks[start:end] = [f"""{entity["text"]}"""] * (end - start)

    print("".join(key for key, _ in groupby(redacted_chunks)))
