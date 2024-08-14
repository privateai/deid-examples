# Introduction

This repository contains examples that showcase how to use the Private AI REST API, for both Python and JS. The API allows for PII to be found in text and then replaced with redaction markers or synthetic PII. The system supports over [50 entity types](https://docs.private-ai.com/entities/), such as Credit Card information and Social Security numbers across [50 languages](https://docs.private-ai.com/languages/). The [documentation](https://docs.private-ai.com/introduction) and the [API reference](https://docs.private-ai.com/reference/latest/operation/process_text_v3_process_text_post/) are available from Private AI's website.

## How to get access

Get a [Community API key here](https://portal.private-ai.com/)

For further information & access to the container feel free to [contact us](https://www.private-ai.com/da2t).

## Setup

Private AI's service is primarily delivered via a self-hosted container. Please follow the [setup instructions](https://docs.private-ai.com/installation/) to get started.

It is also possible to use the Private AI cloud endpoint located at [https://portal.private-ai.com/](https://portal.private-ai.com/).

## What are these examples?

In the [JS](./js/examples/) folder where have common api call examples and use cases built in javascript. In the [python](./python/examples/) folder we have the same examples expressed in python. If you are interested in our [PrivateGPT](https://www.private-ai.com/products/privategpt-headless/) to work securely with LLMs, you should check out the [LLMs](./python/LLM%20Examples/) folder for some really cool stuff!
