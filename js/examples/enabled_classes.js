const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post("http://localhost:8080/deidentify_text", {
    text: "My name is John and my friend is Grace and we live in Barcelona",
    key: process.env.API_KEY,
    enabled_classes: ["AGE", "LOCATION"],
  })
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );

// Example with async/await
const enabled_classes = async () => {
  try {
    const result = await axios.post("http://localhost:8080/deidentify_text", {
      text: "My name is John and my friend is Grace and we live in Barcelona",
      key: process.env.API_KEY,
      enabled_classes: ["AGE", "LOCATION"],
    });
    console.log(result.data);
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

enabled_classes();
