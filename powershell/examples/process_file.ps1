# This script presumes you are running the Private AI container locally on port 8080
# If this is not the case, update the uri below
$uri = "http://localhost:8080/process/files/base64"

# The example uses a PDF in an input folder
$filename = "C:\input\sample.pdf"

# Read the file and base64 encode it
$base64file = [Convert]::ToBase64String([IO.File]::ReadAllBytes($filename))

# Modify the content_type to suit the file you are sending
$body = @{
    'file' = @{
        'data' = $base64file
        'content_type' = 'application/pdf'
    }
} | ConvertTo-Json

# POST the file to be de-identified and collect the response
$response = Invoke-WebRequest -Uri $uri -Body $body -ContentType application/json -Method POST | ConvertFrom-Json

# Output the de-identified text to a file
$response.processed_text | Out-File "C:\output\sample.log"

# Base64 decode the de-identified file and store it in the output folder
[IO.File]::WriteAllBytes("C:\output\redacted-sample.pdf", [Convert]::FromBase64String($response.processed_file))
