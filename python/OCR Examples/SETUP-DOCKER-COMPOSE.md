## Deployment with Cloud Azure OCR Services

Private AI DEID container can be configured to use cloud or on-prem version of Azure OCR service. This section shows how to configure the DEID container with cloud Azure OCR service.

1. Create a `docker-compose.yml` file in your preferred text editor.
2. Configure the DEID service and Azure OCR using one of the options below.

:::info Note

The instructions for running the container are provided in the form of a `docker-compose.yml` file for easy readability. Alternatively, you can choose to run the container using the `docker run` command.

For cloud-based Azure OCR services, the only changes required will be in the `PAI_OCR_SYSTEM` and `PAI_AZ_*` environment variables. If you are using the container version of Azure OCR services, you will need to run the Azure OCR container alongside the DEID container.

:::

:::info Note

For production deployments, we recommend using Kubernetes for managing the containers.

:::

### **Option 1 - DEID Container with cloud Azure Computer Vision Service**

This section shows how to configure the DEID container with cloud Azure Computer Vision Service.

```yaml
version: '3.8'
services:
  deid_service:
    image: crprivateaiprod.azurecr.io/deid:gpu
    shm_size: "4g"
    container_name: deid_container
    tty: true
    environment:
      - PAI_OCR_SYSTEM=azure_computer_vision
      - PAI_AZ_COMPUTER_VISION_URL=<Azure Computer Vision Service URL>
      - PAI_AZ_COMPUTER_VISION_KEY=<Azure Computer Vision Key>
      - PAI_OUTPUT_FILE_DIR=<output file directory>
    ports:
      - "8080:8080"
    # Input and output directories are only required when using URI file processing
    volumes:
      - <path to license.json>:/app/license/license.json
      - <input file directory>:<input file directory>
      - <output file directory>:<output file directory>  # This directory should be same as PAI_OUTPUT_FILE_DIR
    # comment out this section if you're using a CPU version of deid container.
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Replace placeholders (e.g., `<Azure Computer Vision Service URL>`) with your actual service details.

### **Option 2 - DEID Container with cloud Azure Document Intelligence Service**

This section shows how to configure the DEID container with cloud Azure Document Intelligence Service.

```yaml
version: '3.8'
services:
  deid_service:
    image: crprivateaiprod.azurecr.io/deid:gpu
    shm_size: "4g"
    container_name: deid_container
    tty: true
    environment:
      - PAI_OCR_SYSTEM=azure_doc_intelligence
      - PAI_AZ_DOCUMENT_INTELLIGENCE_URL=<Azure Document Intelligence Service URL>
      - PAI_AZ_DOCUMENT_INTELLIGENCE_KEY=<Azure Document Intelligence Key>
      - PAI_OUTPUT_FILE_DIR=<output file directory>
    ports:
      - "8080:8080"
    # Input and output directories are only required when using URI file processing
    volumes:
      - <path to license.json>:/app/license/license.json
      - <input file directory>:<input file directory>
      - <output file directory>:<output file directory>  # This directory should be same as PAI_OUTPUT_FILE_DIR
    # comment out this section if you're using a CPU version of deid container.
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Replace placeholders (e.g., `<Azure Document Intelligence Service URL>`) with your actual service details.

## Deployment with On-Premise Azure OCR Services

:::info Note

Currently, only the Azure Computer Vision Service can be used on-premise with the Private AI DEID service.

:::

Private AI DEID container can be configured to use cloud or on-prem version of Azure OCR service. This section shows how to configure the DEID container with on-premise Azure Computer Vision Service.

1. Create a `docker-compose.yml` file in your preferred text editor.
2. Configure the DEID service and Azure OCR using one of the options below.

### **Option 3 - DEID Container with On-Premise Azure Computer Vision Service**

This section shows how to configure the DEID container with on-premise Azure Computer Vision Service.

```yaml
version: '3.8'
services:
  deid_service:
    image: crprivateaiprod.azurecr.io/deid:gpu
    shm_size: "4g"
    container_name: deid_container
    tty: true
    environment:
      - PAI_OCR_SYSTEM=azure
      - PAI_AZ_COMPUTER_VISION_URL=http://azure_vision_service:5000
      - PAI_AZ_COMPUTER_VISION_KEY=<Azure Computer Vision Key>
      - PAI_OUTPUT_FILE_DIR=<output file directory>
    ports:
      - "8080:8080"
    # Input and output directories are only required when using URI file processing
    volumes:
      - <path to license.json>:/app/license/license.json
      - <input file directory>:<input file directory>
      - <output file directory>:<output file directory>  # This directory should be same as PAI_OUTPUT_FILE_DIR
    # comment out this section if you're using a CPU version of deid container.
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  azure_vision_service:
    image: mcr.microsoft.com/azure-cognitive-services/vision/read:latest
    container_name: azure_vision_container
    tty: true
    environment:
      - Eula=accept
      - Billing=<Azure Computer Vision Resource Endpoint>
      - ApiKey=<Azure Computer Vision Resource Key>
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
```

For further details on the Azure Computer Vision container please refer to the [Azure Documentation](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/computer-vision-how-to-install-containers).


## Start the Containers

Open a terminal and navigate to the directory containing your `docker-compose.yml` file. Run the following command to start the containers:

```bash
docker compose -f docker-compose.yml up
```

## Verify Operation

Once the containers are running, you can verify their operation by accessing the DEID service's exposed port (e.g., `http://localhost:8080`) and performing a test OCR operation on your documents or images.
