/**
 * Example script to illustrate how to make API calls to the Private AI Docker
 * container to deidentify text using the fake entity generation feature.
 *
 * To use this script, please start the Docker container locally, as per the
 * instructions at https://private-ai.com/docs/installation.
 *
 * In order to use the API key issued by Private AI, you can run the script as
 * `API_KEY=<your key here> node fake_entity_generation.js` or you can define a
 * `.env` file which has the line `API_KEY=<your key here>`.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post("http://localhost:8080/deidentify_text", {
    text: "My name is John and my friend is Grace and we live in Barcelona",
    key: process.env.API_KEY,
    fake_entity_accuracy_mode: "standard",
  })
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );

// Example with async/await
const fake_entity_generation = async () => {
  try {
    const result = await axios.post("http://localhost:8080/deidentify_text", {
      text: "My name is John and my friend is Grace and we live in Barcelona",
      key: process.env.API_KEY,
      fake_entity_accuracy_mode: "standard",
    });
    console.log(result.data);
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

fake_entity_generation();
