import argparse
import json
import sys

import demo_config
from openai import OpenAI
from privateai_client import PAIClient, request_objects

# Initialize parser
parser = argparse.ArgumentParser(description="A Python script with a model parameter.")
parser.add_argument("-m", "--model", required=True, help="Specify the model to use.")
args = parser.parse_args()

# Initialize the openai client
openai_client = OpenAI(api_key=demo_config.openai["API_KEY"])

# initialize the privateai client
PRIVATEAI_SCHEME = "https"
PRIVATEAI_HOST = demo_config.privateai["PROD_URL"]
pai_client = PAIClient(PRIVATEAI_SCHEME, PRIVATEAI_HOST)
pai_client.add_api_key(demo_config.privateai["PROD_KEY"])


############ Vertex AI Config ##########
import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair

vertexai.init(
    project=demo_config.vertex["PROJECT"], location=demo_config.vertex["LOCATION"]
)
chat_model = ChatModel.from_pretrained("chat-bison@001")
parameters = {"temperature": 0.8, "max_output_tokens": 256, "top_p": 0.8, "top_k": 40}

############ Cohere config #############
import cohere

co = cohere.Client(demo_config.cohere["API_KEY"])

models = ["openai", "cohere", "vertexai"]


def prompt_chat_gpt(text):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": text}]
    )
    return completion.choices[0].message.content


def prompt_vertex_ai(prompt, context):
    # call vertexAI
    chat = chat_model.start_chat(context=context, examples=[])
    parameters = {
        "temperature": 0.8,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40,
    }
    completion = chat.send_message(f"{prompt}", **parameters)
    return completion.text


def prompt_cohere(prompt):
    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=300,
        temperature=0.9,
        k=0,
        stop_sequences=[],
        return_likelihoods="NONE",
    )
    return response.generations[0].text


def private_prompt(prompt, raw_text, model):
    completions = (
        {}
    )  # a dict that maintains the history of the raw data, redaction, and completions
    ################################################
    ############ Identify and Redact ###############
    ################################################
    completions["raw_text"] = raw_text
    redaction_request_obj = request_objects.process_text_obj(text=[raw_text])
    redaction_response_obj = pai_client.process_text(redaction_request_obj)

    ################################################
    ############ Store redactions  #################
    ################################################
    deidentified_text = redaction_response_obj.processed_text[0]
    completions["redacted_text"] = deidentified_text
    entity_list = redaction_response_obj.get_reidentify_entities()

    ################################################
    ############ Generate Completion ###############
    ################################################
    completions["redacted_completion"] = []  # create empty list to hold completions
    completions["reidentified_completion"] = []  # same thing for re-identifications
    match model:
        case "openai":
            print("OPENAI SELECTED")
            llm_response = prompt_chat_gpt(prompt + deidentified_text)
            completions["redacted_completion"].append(
                {"model": model, "completion": llm_response}
            )
        case "vertexai":
            print("VertexAI/Bard selected")
            llm_response = prompt_vertex_ai(prompt, deidentified_text)
            completions["redacted_completion"].append(
                {"model": model, "completion": llm_response}
            )
        case "cohere":
            print("Cohere selected")
            llm_response = prompt_cohere(prompt + deidentified_text)
            completions["redacted_completion"].append(
                {"model": model, "completion": llm_response}
            )
        case "all":
            completions["redacted_completion"].append(
                {
                    "model": "openai",
                    "completion": prompt_chat_gpt(prompt + deidentified_text),
                }
            )
            completions["redacted_completion"].append(
                {
                    "model": "vertexai",
                    "completion": prompt_vertex_ai(prompt, deidentified_text),
                }
            )
            completions["redacted_completion"].append(
                {
                    "model": "cohere",
                    "completion": prompt_cohere(prompt + deidentified_text),
                }
            )
        case _:
            print("No valid model selected, so using chatgpt")
            llm_response = prompt_chat_gpt(prompt + deidentified_text)
            completions["redacted_completion"].append(
                {"model": "openai", "completion": llm_response}
            )

    ################################################
    ############ Call the reidentify Route #########
    ################################################

    for completion in completions["redacted_completion"]:
        reidentification_request_obj = request_objects.reidentify_text_obj(
            processed_text=[completion["completion"]], entities=entity_list
        )
        reidentification_response_obj = pai_client.reidentify_text(
            reidentification_request_obj
        )
        completions["reidentified_completion"].append(
            {
                "model": completion["model"],
                "re-identified": reidentification_response_obj.body[0],
            }
        )
    return completions


raw_sample_text = """
On May 17, 2023, the U.S. District Court for the Southern District of New York entered a final consent judgment against Sam A. Antar, who the SEC previously charged with defrauding investors, many of whom were his friends and acquaintances in a Syrian Jewish community in New Jersey.
The SEC's s complaint, alleged that Antar, of New York, New York, engaged in a fraudulent scheme that deceived numerous investors out of more than $550,000 while claiming he would invest in shares of companies that were not yet public, and then sell those shares to already-identified buyers for a premium in a short period of time. In reality, according to the complaint, Antar never used investor funds to purchase shares of emerging companies, or to make any other investment. Instead, Antar spent investor funds gambling, making gifts to family members, paying for his daughter's wedding, and making Ponzi-like payments to some early investors.
The final judgment permanently enjoins Antar from violating the antifraud provisions of the federal securities laws, Section 17(a) of the Securities Act of 1933 and Section 10(b) of the Securities Exchange Act of 1934 and Rule 10b-5 thereunder. The judgment also orders Antar to pay disgorgement of $567,000 and prejudgment interest of $88,754, with offsets permitted for amounts Antar pays pursuant to a restitution order in a parallel criminal action.
In a parallel criminal action, the New Jersey Office of the Attorney General Division of Criminal Justice filed criminal charges against Antar. On April 22, 2022, Antar pled guilty to certain of the charges and on December 9, 2022, was sentenced to three years in prison and ordered to pay restitution of $15,000.
"""

completions = private_prompt("summarize this: ", raw_sample_text, args.model)
print(completions["redacted_completion"])
print("\n**************************\n")
print(completions["reidentified_completion"])
print(json.dumps(completions))
