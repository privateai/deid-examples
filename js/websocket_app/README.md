# Private AI Websocket Example

This example showcases a practical implementation of real-time data redaction using Private AI's websocket API within a React web application.


## Requirements

Ensure you have Node.js installed locally with version v20.16.0 or greater. For running multiple versions of node, it is recommended to install and use [NVM](https://github.com/nvm-sh/nvm).

You also must be running the Private AI container. This script presumes that the container is running locally. This script was tested with container version 3.7.0.

## Setup

```bash
git clone https://github.com/privateai/deid-examples/js/websocket_app/
cd websocket_app
```

Install it and run:

```bash
npm install
npm run dev
```


## The Idea Behind This Example
By leveraging Private AI's capabilities, the example demonstrates how developers can integrate advanced privacy-preserving features into their applications. This is particularly relevant for scenarios requiring the processing of sensitive information, such as personal identifiers, in real-time, ensuring that data privacy is maintained without compromising on user experience. 


## What's Next?

-   Explore the code of this example
-   Read the [WebSocket Guide](https://docs.private-ai.com/websocket/)
-   Discover the [API](https://docs.private-ai.com/reference/latest/operation/process_text_v3_process_text_post/)
