# Azure ACI Deployment Instructions

This folder includes an ARM template and a sample parameters file to deploy Limina DEID to Azure Container Instances.

## Files

- `azuredeploy.json` - ARM template defining:
  - Azure Container Instance container group
  - Azure Storage account
  - Azure File shares for `license`
  - public endpoint for the container  - 
- `azuredeploy.parameters.sample.json` - sample parameter values for the deployment

## Before you deploy

1. Copy `azuredeploy.parameters.sample.json` to `azuredeploy.parameters.json` and update `azuredeploy.parameters.json`:
   - `containerImage`: your Limina DEID container image URI
   - `location`: desired Azure region, for example `eastus`
   - `storageAccountName`: unique Azure storage account name
   - `storageAccountSku`: Validate that the correct storage account SKU shortform is used
   - `dnsNameLabel`: DNS label for the public ACI endpoint
   - Optionally update `environmentName`, `containerGroupName`, `cpuCores`, and `memoryInGb`

2. Make sure the `license` file share contains `license.json` after deployment.

## Deploy using Azure CLI

From this folder, run:

```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json \
  --parameters registryUsername=<username> registryPassword=<password>
```
Replace:
- `<username>` - your container registry username
- `<password>` - your container registry password or access token

These values come from the Limina customer portal or from your own local ACR 

## After deployment

- The deployment creates a public ACI endpoint.
- Use the output FQDN and port `8080` to call the service.
- Example URL:

```text
http://<dnsNameLabel>-<region>-azurecontainer.io:8080
```

## Storage shares

The template creates three Azure File shares:

- `license` → mounted at `/app/license`

Upload your `license.json` to the `license` share before or after deployment.

## Notes

- The ACI container group is publicly accessible via the DNS label.
- Adjust `cpuCores` and `memoryInGb` in the parameters file to match the container's requirements.
