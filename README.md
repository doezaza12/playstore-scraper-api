# Playstore-scraper-API
This project just the bridge between API and scraper lib from [google-play-scraper](https://github.com/JoMingyu/google-play-scraper) \
trying to avoid TOO MANY REQUEST (429)

![udacity-datamodeling-scraper-api-strategy drawio](https://user-images.githubusercontent.com/45708687/209457355-caba991a-151e-4b34-883b-c46d1dd24201.png)

#### Experiment
- Using pyspark in local to make request with Dataframe + UDF
- Implement exponential backoff with maximum retry window = 60s (in case, we are switching public IP to change source request IP in server perspective so it will jitter for shot moment and to retry 429 request)
- The first 429 will appear around 180+ consecutive requests (with throttling = 200)
- with pyspark local, it will make around 200 requests per min.

#### Prerequisite
- ECR in case, you want to pull image. If you plan to build and run it directly on the instance then you can skip.
- Lambda for rotating EIP (source public IP)
- IAM permission (I will suggest only AWS managed policy to make it simple but in real scenario please use customer managed policy)
    - for EC2, you can attach AWS managed policy ["AmazonEC2ContainerRegistryReadOnly", "AWSLambdaRole"]
    - for Lambda, you can attach AWS managed policy ["AmazonEC2FullAccess", "AWSLambdaExecute", "AWSLambda_FullAccess"]
- Deploy lambda code in /lambda
- Lambda must grant permission for the EC2 role to invoke itself
- Increase lambda timeout from default 3s to at least 10s

#### How to run
1. run ec2 instance **disable auto assign public IP in network section** (from experiment, hosting docker on amazon-linux-2 m5.large is stable *please avoid burst type)
- assign instance profile (IAM role from prerequisite) 
- allow security group on target port (default from Dockerfile = 8000 TCP, allow additional 22 SSH port)
2. create additional ENI in the same subnet of the instance and attach to the instance and using the same security group as the instance
3. allocate 2 EIPs and associate both to the ENIs (primary from #1 and secondary from #2)
4. ssh to the instance using EIP from secondary EIP #2 (in case, you need to keep ssh session) and install docker inside ec2 instance
5. pull docker from ECR or build from Dockerfile
6. run docker with cmd, you must add --net=host  when run this container (otherwise, docker default network will not be accessed eth1 from secondary ENI)
```bash
docker run --net=host -d -p 8000:8000 your-docker-image
```
7. Config lambda environment vairables 
    - CURRENT_ALLOCATION_ID	eipalloc-0f6cdxxxxx (get from EIP console that relate to ENI #1)
    - CURRENT_ASSOCIATION_ID	eipassoc-04ebbxxxx (get from EIP console that relate to ENI #1)
    - PRIMARY_NETWORK_INTERFACE	eni-05e8310fxxxxxx (get from primary ENI ec2 instance after launch. in other word, ENI #1)
    - THIS_FUNCTION_NAME	lambda-eip-switching (name of your lambda function from prerequisite)
8. For make API request, must use EIP #2 for entry point