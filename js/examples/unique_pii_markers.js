/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify text using the unique PII markers feature.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY and URL
dotenv.config();

// Example without async/await
function sync_unique_pii_markers() {
  console.log("***** Sync unique PII markers *****")
  axios.post(
    `${process.env.PAI_URL}/v3/process/text`,
    {
      text: ["My name is John and my friend is Grace and we live in Barcelona"],
      link_batch: false,
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
const async_unique_pii_markers = async () => {
  console.log("***** Async unique PII markers *****")
  try {
    const result = await axios.post(
      `${process.env.PAI_URL}/v3/process/text`,
      {
        text: [
          "My name is John and my friend is Grace and we live in Barcelona",
        ],
        link_batch: false,
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

// sync_unique_pii_markers();
async_unique_pii_markers();
