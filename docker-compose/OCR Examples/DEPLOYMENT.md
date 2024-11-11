## Deployment with Cloud Azure OCR Services

Private AI DEID container can be configured to use cloud or on-prem version of Azure OCR service. This example shows how to configure the DEID container with cloud Azure OCR service.

1. Create a `docker-compose.yml` using samples in this directory.
2. Configure the DEID service and Azure OCR using one of the options below.

The instructions for running the container are provided in the form of a `docker-compose.yml` file for easy readability. Alternatively, you can choose to run the container using the `docker run` command.

For cloud-based Azure OCR services, the only changes required will be in the `PAI_OCR_SYSTEM` and `PAI_AZ_*` environment variables. If you are using the container version of Azure OCR services, you will need to run the Azure OCR container alongside the DEID container.

For production deployments, we recommend using Kubernetes for managing the containers.

### **Option 1 - DEID Container with cloud Azure Computer Vision Service**

docker-compose-deid-cloud-cv.yml

### **Option 2 - DEID Container with cloud Azure Document Intelligence Service**

docker-compose-deid-cloud-doc-intelligence.yml

### **Option 3 - DEID Container with On-Premise Azure Computer Vision Service**

docker-compose-deid-local-cv.yml

For further details on the Azure Computer Vision container please refer to the [Azure Documentation](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/computer-vision-how-to-install-containers).

## Start the Containers

Open a terminal and navigate to the directory containing your `docker-compose.yml` file. Run the following command to start the containers:

```bash
docker compose -f docker-compose.yml up
```

## Verify Operation

Once the containers are running, you can verify their operation by accessing the DEID service's exposed port (e.g., `http://localhost:8080`) and performing a test OCR operation on your documents or images.

