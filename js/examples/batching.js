/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify text using the batching feature.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY and URL
dotenv.config();

// Example without async/await
function sync_batching() {
  console.log("***** Sync batching *****");
  axios.post(
    `${process.env.PAI_URL}/v3/process/text`,
    {
      text: [
        "Hi, my name is Penelope, could you tell me your phone number please?",
        "Sure, x234",
        "and your DOB please?",
        "fourth of Feb nineteen 86",
      ],
      link_batch: true,
      entity_detection: {
        return_entity: true,
      },
      processed_text: {
        type: "MARKER",
        pattern: "[UNIQUE_NUMBERED_ENTITY_TYPE]",
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

// Example with async/await
async function async_batching() {
  console.log("***** Async batching *****");
  try {
    const result = await axios.post(
      `${process.env.PAI_URL}/v3/process/text`,
      {
        text: [
          "Hi, my name is Penelope, could you tell me your phone number please?",
          "Sure, x234",
          "and your DOB please?",
          "fourth of Feb nineteen 86",
        ],
        link_batch: true,
        entity_detection: {
          return_entity: true,
        },
        processed_text: {
          type: "MARKER",
          pattern: "[UNIQUE_NUMBERED_ENTITY_TYPE]",
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

// sync_batching();
async_batching();
