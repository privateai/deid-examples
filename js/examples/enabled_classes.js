/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify text using the enabled classes feature.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY and URL
dotenv.config();

// Example without async/await
function sync_enabled_classes() {
  console.log("***** Sync enabled classes *****");
  axios.post(
    `${process.env.PAI_URL}/process/text`,
    {
      text: ["My name is John and my friend is Grace and we live in Barcelona"],
      link_batch: false,
      entity_detection: {
        return_entity: true,
        entity_types: [
          {
            type: "ENABLE",
            value: ["AGE", "LOCATION"],
          },
        ],
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
async function async_enabled_classes() {
  console.log("***** Async enabled classes *****");
  try {
    const result = await axios.post(
      `${process.env.PAI_URL}/process/text`,
      {
        text: [
          "My name is John and my friend is Grace and we live in Barcelona",
        ],
        link_batch: false,
        entity_detection: {
          return_entity: true,
          entity_types: [
            {
              type: "ENABLE",
              value: ["AGE", "LOCATION"],
            },
          ],
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

// sync_enabled_classes();
async_enabled_classes();
