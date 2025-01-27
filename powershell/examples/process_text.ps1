# This script presumes you are running the Private AI container locally on port 8080
# If this is not the case, update the uri below
$uri = "http://localhost:8080/process/text"

$body = @{
    'text' = @(
        "This is some sample text for Company A"
        "This sample was prepared by John Smith"
    )
} | ConvertTo-Json

# POST the body to the Private AI endpoint to be de-identified and collect the response
$response = Invoke-WebRequest -Uri $uri -Body $body -ContentType application/json -Method POST

# Print the response
$response

# Print the contents of the response
$response.Content
