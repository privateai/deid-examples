# This script presumes you are running the Private AI container locally on port 8080
# If this is not the case, update the uri below
$uri = "http://localhost:8080/process/files/base64"

# Put all the files you'd like to de-identify in an input folder
$inputDir = "C:\input"

# Create an output folder to collect all the de-identified files and logs
$outputDir = "C:\output"

# This content map will help with converting the files by extentions to thier MIME type
$contentType = @{
    ".pdf" = "application/pdf"
    ".json" = "application/json"
    ".xml" = "application/xml"
    ".csv" = "text/csv"
    ".doc" = "application/msword"
    ".docx" = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ".eml" = "message/rfc822"
    ".txt" = "text/plain"
    ".xls" = "application/vnd.ms-excel"
    ".xlsx" = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ".ppt" = "application/vnd.ms-powerpoint"
    ".pptx" = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ".dcm" = "application/dicom"
    ".jpg" = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".tif" = "image/tiff"
    ".tiff" = "image/tiff"
    ".png" = "image/png"
    ".bmp" = "image/bmp"
    ".wav" = "audio/wav"
    ".mp3" = "audio/mpeg"
    ".mp4" = "audio/mp4"
    ".m4a" = "audio/m4a"
    ".webm" = "audio/webm"
}

# Iterate through each file in the input folder
Get-ChildItem $inputDir | ForEach-Object {

    # Read the file and base64 encode it
    $base64file = [Convert]::ToBase64String([IO.File]::ReadAllBytes($_.FullName))

    $body = @{
        'file' = @{
            'data' = $base64file
            'content_type' = $contentType[$_.Extension]
        }
    } | ConvertTo-Json

    # POST the file to be de-identified and collect the response
    $response = Invoke-WebRequest -Uri $uri -Body $body -ContentType application/json -Method POST | ConvertFrom-Json

    # Set put the de-identified data log and output file names
    $outputLog = $_.BaseName + ".log"
    $outputLogPath = Join-Path $outputDir $outputLog
    $outputFile = "redacted-" + $_.Name
    $outputFilePath = Join-Path $outputDir $outputFile

    # Output the de-identified text to a file
    $response.processed_text | Out-File $outputLogPath

    # Base64 decode the de-identified file and store it in the output folder
    [IO.File]::WriteAllBytes($outputFilePath, [Convert]::FromBase64String($response.processed_file))
}
