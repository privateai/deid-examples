/**
 * Example script to illustrate how to make API calls to the Private AI Docker
 * container to deidentify text using the non-unique PII markers feature.
 *
 * To use this script, please start the Docker container locally, as per the
 * instructions at https://private-ai.com/docs/installation.
 *
 * In order to use the API key issued by Private AI, you can run the script as
 * `API_KEY=<your key here> node non_unique_pii_markers.js` or you can define a
 * `.env` file which has the line `API_KEY=<your key here>`.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post(
    "http://localhost:8080/v3/process/text",
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
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );

// Example with async/await
const non_unique_pii_markers = async () => {
  try {
    const result = await axios.post(
      "http://localhost:8080/v3/process/text",
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

    console.log(data);
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

non_unique_pii_markers();
