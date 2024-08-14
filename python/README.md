# Introduction

This folder contains a set of python examples for interacting with the Private AI API. By default the scripts will interact with the Community APIs, but you can also use these as the basis for connecting to the Professional APIs, or to your own running container.

## Setup

1. Ensure you have python 3.12 or later installed. It is recommended to use [pyenv](https://github.com/pyenv/pyenv) if you have multiple python projects with different versions.
1. Run `pip install -U pip` to ensure you have the latest version of the package installer for python.
1. Run `pip install -r requirements.txt` to install all the packages needed to run the examples.
1. Get your Community API key from the Private AI [Customer Portal](https://portal.private-ai.com).
1. Copy the `.env.example` file to `.env` and update it with your Community API key.

## Running the examples

You can run any example in the `examples` folder simply by running `python examples\<example file>`. For example, to try the link batch example, run `python examples\async_call.js`.
