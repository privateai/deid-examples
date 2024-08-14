# Introduction

This folder contains a set of javascript examples for interacting with the Private AI API. By default the scripts will interact with the Community APIs, but you can also use these as the basis for connecting to the Professional APIs, or to your own running container.

## Setup

1. Ensure you have installed Node.js v20.16 or greater. It is recommended to use [Node Version Manager](https://github.com/nvm-sh/nvm) if you have multiple node projects of different levels.
1. Run `npm install` to install the required packages from `package.json`.
1. Copy the `.env.example` file to `.env` and update the variables with your own API key and Private AI API URL.

## Running the examples

You can run any example in the `examples` folder simply by running `node examples\<example file>`. For example, to try the link batch example, run `node examples\batching.js`.
