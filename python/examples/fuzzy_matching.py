# Example script to illustrate how to make calls to the Private AI API to
# deidentify text and match the detected entites against a list of words.
# Mask the detected entities if the Damerau Lenvenshtien  distance of an
# entity is less than a certain threshold.

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

        def __eq__(self, other):
            """
            Compares two NotComparable instances for equality.

            This method is overridden to ensure that two NotComparable objects with identical values are not 
            considered equal. This is essential because we want each character to be treated as a unique 
            instance, even if they share the same value.

            Args:
                other (object): The object to compare this instance with.

            Returns:
                bool: Always returns False to ensure non-comparability.
            """
            return False


samples = [
    {
        "text": "The CEO of the tech company met with the investor to discuss upcoming innovations. John, the company's marketing consultant, provided valuable insights on market trends and potential risks, which helped shape the final strategy for the next quarter.",
        "entity_type": "OCCUPATION",
        "entity_values": ["CEO", "investor"],
    },
    {
        "text": "Robert, the CEO of an ambitious startup, and Emily, a high-profile invetsor, met to chart out a potential exit strategy. The conversation ranged from IPO prospects to acquisition opportunities, aiming to maximize returns while preserving company culture.",
        "entity_type": "OCCUPATION",
        "entity_values": ["CEO", "investor"]
    },
    {
        "text": "Sarah, a seasoned project manager, coordinated efforts between multiple departments to launch a new product. Her leadership ensured that deadlines were met, and the team received commendation for their hard work and timely delivery.",
        "entity_type": "OCCUPATION",
        "entity_values": ["CEO", "investor"]
    }
]

sample_entity_type_selector = request_objects.entity_type_selector_obj(type="ENABLE", value=["NAME", "OCCUPATION"])
sample_entity_detection = request_objects.entity_detection_obj(entity_types=[sample_entity_type_selector])

for sample in samples:
    text, entity_type, entity_values = sample["text"], sample["entity_type"], sample["entity_values"]

    process_text_request = request_objects.ner_text_obj(
        text=[text],
        entity_detection=sample_entity_detection
    )
    response = client.ner_text(process_text_request)
    entities = response.entities[0]

    redacted_chunks = [NotComparable(c) for c in text]

    threshold = 2
    masking_character = '#'
    for entity in entities:
        # calculate Damerau Lenvenshtien distance between the detected entities and each word
        distances = [damerau_levenshtein_distance(entity["text"], value) for value in entity_values]

        # get the minimum distance
        min_dist = min(distances)

        # get the index of the word with the minimum distance
        min_dist_idx = distances.index(min_dist)

        start = entity["location"]["stt_idx"]
        end = entity["location"]["end_idx"]

        # Mask the entity if the distance is less than the threshold
        if entity["label"] == entity_type and min_dist <= threshold:
            redacted_chunks[start:end] = [f"""{masking_character * len(entity["text"])}"""] * (end - start)
        # Redact the entity otherwise
        else:
            redacted_chunks[start:end] = [f"""[{entity["label"]}]"""] * (end - start)

    print("".join(key for key, _ in groupby(redacted_chunks)))


# Output:
# 1: Illustrates masking of the entities "CEO" and "investor" using the "#" character, while other detected entities are redacted with their corresponding labels.
# "The ### of the tech company met with the ######## to discuss upcoming innovations. [NAME], the company's [OCCUPATION], provided valuable insights on market trends and potential risks, which helped shape the final strategy for the next quarter."
#
## 2: Shows masking of the entities "CEO" and "investor" via fuzzy matching based on the `entity_type`, with other detected entities redacted using their labels.
# "[NAME], the ### of an ambitious startup, and [NAME], a high-profile ########, met to chart out a potential exit strategy. The conversation ranged from IPO prospects to acquisition opportunities, aiming to maximize returns while preserving company culture."
#
# 3: Highlights redaction of detected entities using their labels. Masking is omitted since "project manager" is not in the list of target entities, `entity_values`.
# "[NAME], a seasoned [OCCUPATION], coordinated efforts between multiple departments to launch a new product. Her leadership ensured that deadlines were met, and the team received commendation for their hard work and timely delivery."
