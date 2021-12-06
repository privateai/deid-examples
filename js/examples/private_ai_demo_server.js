/**
 * Example script to illustrate how to make API calls to the Private AI Demo
 * Server to deidentify text.
 *
 * To use this script, please start the Docker container locally, as per the
 * instructions at https://private-ai.com/docs/installation.
 *
 * In order to use the API key issued by Private AI, you can run the script as
 * `API_KEY=<your key here> node enabled_classes.js` or you can define a `.env`
 * file which has the line `API_KEY=<your key here>`.
 */
const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post("https://demoprivateai.com", {
    text: "My name is John and my friend is Grace",
    key: process.env.API_KEY,
  })
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );

// Example with async/await
const private_ai_demo_server = async () => {
  try {
    const result = await axios.post("https://demoprivateai.com", {
      text: "My name is John and my friend is Grace",
      key: process.env.API_KEY,
    });
    console.log(result.data);
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

private_ai_demo_server();
