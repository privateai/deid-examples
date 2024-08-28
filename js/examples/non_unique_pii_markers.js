/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify text using the non-unique PII markers feature.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY and URL
dotenv.config();

// Example without async/await
function sync_non_unique_pii_markers() {
  console.log("***** Sync non-unique PII markers *****");
  axios.post(
    `${process.env.PAI_URL}/process/text`,
    {
      text: ["My name is John and my friend is Grace"],
      link_batch: false,
      entity_detection: {
        return_entity: true,
      },
      processed_text: {
        type: "MARKER",
        pattern: "[BEST_ENTITY_TYPE]",
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
async function async_non_unique_pii_markers() {
  console.log("***** Async non-unique PII markers *****");
  try {
    const result = await axios.post(
      `${process.env.PAI_URL}/process/text`,
      {
        text: ["My name is John and my friend is Grace"],
        link_batch: false,
        entity_detection: {
          return_entity: true,
        },
        processed_text: {
          type: "MARKER",
          pattern: "[BEST_ENTITY_TYPE]",
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

// sync_non_unique_pii_markers();
async_non_unique_pii_markers();
