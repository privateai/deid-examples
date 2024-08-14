/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify a file.
 */
const axios = require("axios");
const dotenv = require("dotenv");
const fs = require("fs");

// Use to load the API_KEY and URL
dotenv.config();

const b64file = fs.readFileSync("examples/sample.txt", {encoding: "base64"});

// Example without async/await
function sync_process_file_base64() {
  console.log("***** Sync process file base64 *****");
  axios.post(
    `${process.env.PAI_URL}/v3/process/files/base64`,
    {
      file: {
        data: b64file,
        content_type: "text/plain",
      },
    },
    {
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": process.env.API_KEY,
      },
    }
  )
  .then((result) => console.log(JSON.stringify(result.data, undefined, 2)))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );
}

async function async_process_file_base64() {
  console.log("***** Async process file base64 *****");
  try {
    const result = await axios.post(
      `${process.env.PAI_URL}/v3/process/files/base64`,
      {
        file: {
          data: b64file,
          content_type: "text/plain",
        },
      },
      {
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": process.env.API_KEY,
        },
      }
    );

    const { data } = result;

    console.log(JSON.stringify(data, undefined, 2));
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

// sync_process_file_base64();
async_process_file_base64();
