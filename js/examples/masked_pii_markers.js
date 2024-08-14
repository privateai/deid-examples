/**
 * Example script to illustrate how to make requests to the Private AI API
 * to deidentify text using the masked PII markers feature.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY and URL
dotenv.config();

// Example without async/await
function sync_masked_pii_markers() {
  console.log("***** Sync masked PII markers *****");
  axios.post(
    `${process.env.PAI_URL}/v3/process/text`,
    {
      text: ["My name is John and my friend is Grace and we live in Barcelona"],
      link_batch: false,
      entity_detection: {
        return_entity: true,
      },
      processed_text: {
        type: "MASK",
        mask_character: "#",
      },
    },
    {
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": process.env.API_KEY,
      },
    }
  )
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );
}

// Example with async/await
async function async_masked_pii_markers () {
  console.log("***** Async masked PII markers *****");
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
          type: "MASK",
          mask_character: "#",
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

// sync_masked_pii_markers();
async_masked_pii_markers();
