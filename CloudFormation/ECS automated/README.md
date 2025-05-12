## Deployment to ECS with CloudFormation template

Private AI DEID container can be configured using a CloudFormation ECS template with your own settings. This document illustrates how to do that by using your production container. In this folder, there are five YAML template files for your setup. Please see [General ECS deployment test using Marketplace demo container image](https://docs.private-ai.com/aws/aws_with_ecs_automated_guide/) 

## Files included

1. cluster.yaml
1. main.yaml
1. security-groups.yaml
1. service.yaml
1. values.yaml
(Other necessary yaml files are stored in our s3 and referenced automatically)

## Preparation

### Setup AWS CLI

Please confirm you have aws cli in your deployment environment.

### s3 bucket to store these yaml files and your Private AI license file

In this sample, an S3 bucket is required to store the files as shared templates in your environment.

### pull and store Private AI container image to ECR

In this sample, it is assumed that your Private AI container image has been retrieved in advance and stored in ECR. Please see [our document](https://docs.private-ai.com/aws/aws_with_ecs_manually_guide/#5-create-ecr-repository-and-upload-private-ai-container) for more information.

### Configure values.yaml

values.yaml can be used to set your preferred variables for the configuration. This is the only file you need to update, and it can be customized to better suit your setup. Example values include:

- AWS information 
- EC2 instance type
- Memory, disk size
etc..

Please replace all instances of <value> to your desired value.

### Upload yaml and license file to your s3 bucket

The five YAML files listed above, along with your Private AI license file (please rename it to license.json), need to be uploaded to S3 in your environment.

## Run the template

From your AWS CLI, please create stack. It will look like:

aws cloudformation create-stack --stack-name your-private-ai-stack-name --template-url https://your-company-s3-bucket.s3.us-east-1.amazonaws.com/main.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=AdminIpAddress,ParameterValue=0.0.0.0/0 ParameterKey=SSHKeyName,ParameterValue=yourKeyName ParameterKey=TemplateFileBucketUri,ParameterValue=https://your-company-s3-bucket.s3.us-east-1.amazonaws.com

### Note on command line

`AdminIpAddress` should be modified to limit access through SSHKey. 0.0.0.0/0 means it can be accessed from any IP address. e.g. 10.111.111.111/32 means only from this address can connect to EC2 instance later. For SSH key pair creation, please see [this document](https://docs.private-ai.com/aws/aws_with_ecs_automated_guide/#quick-start)

## Confirm the deployment
1. In AWS Console, go to CloudFormation > Stacks. Check all stacks are completed.
1. Check status. Go to Elastic Container Service > Clusters > <Your cluster> > Services > Your service > Health

### Confirm to login to host
1. First, you need to login to bastion. Go to EC2 and find <Your stack> Bastion instance.
1. From `Connect` button, you can grab ssh command sample to login. Also you need to copy your key file to this bastion host.
1. From bastion, you can ssh into your ECS host. <Your stack name> ECS host can be found in Instances.

### Confirm deidentification
1. Login to your bastion.
1. Curl command to check deidentification. The container is exposed via load balancer. (EC2 > Load balancers)
```shell
curl --request POST --url http://<your load balancer>/process/text --header 'Content-Type: application/json' --data '{"text": ["Hello John"]}'
```
