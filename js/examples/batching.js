const axios = require("axios");
const dotenv = require("dotenv");

// Use to load the API_KEY for authentication
dotenv.config();

// Example without async/await
axios
  .post("http://localhost:8080/deidentify_text", {
    text: ["My password is: 4XDX63F8O1", "My password is: 33LMVLLDHNasdfsda"],
    key: process.env.API_KEY,
  })
  .then((result) => console.log(result.data))
  .catch((error) =>
    console.error(
      `The request failed with the status code ${error.response.status}`
    )
  );

// Example with async/await
const batching = async () => {
  try {
    const result = await axios.post("http://localhost:8080/deidentify_text", {
      text: ["My password is: 4XDX63F8O1", "My password is: 33LMVLLDHNasdfsd"],
      key: process.env.API_KEY,
    });
    console.log(result.data);
  } catch (error) {
    console.error(
      `The request failed with the status code ${error.response.status}`
    );
  }
};

batching();
