/**
 * Example script to illustrate how to make API calls to the Private AI Docker
 * container to deidentify text using the enabled classes feature.
 *
 * To use this script, please start the Docker container locally, as per the
 * instructions at https://private-ai.com/docs/installation.
 *
 * In order to use the API key issued by Private AI, you can run the script as
 * `API_KEY=<your key here> node process_file.js` or you can define a `.env`
 * file which has the line `API_KEY=<your key here>`.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post(
    "http://localhost:8080/v3/process/files/uri",
    {
      uri: "https://example.com/example-image.jpeg",
      entity_detection: {
        accuracy: "high",
        return_entity: true,
      },
      pdf_options: { density: 150 },
      audio_options: {
        bleep_start_padding: 0,
        bleep_end_padding: 0,
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

const process_file_uri = async () => {
  try {
    const result = await axios.post(
      "http://localhost:8080/v3/process/files/uri",
      {
        uri: "https://example.com/example-image.jpeg",
        entity_detection: {
          accuracy: "high",
          return_entity: true,
        },
        pdf_options: { density: 150 },
        audio_options: {
          bleep_start_padding: 0,
          bleep_end_padding: 0,
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

process_file_uri();
