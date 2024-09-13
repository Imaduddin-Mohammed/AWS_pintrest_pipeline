# AWS PINTREST PIPELINE
The main motivation behind building this project comes from the idea of pintrest utilising the AWS Cloud to crunch billions of data points everyday to decide how to provide value to its cutomers. 
This project aims at emulating a similar system using the AWS Cloud.

## Milestone 1: Setting up the environment
##### Task 1: Create a remote repository and clone it
- To clone this repository locally run the following command inside your terminal: `git clone https://github.com/Imaduddin-Mohammed/AWS_pintrest_pipeline.git`.
##### Task 2: Set up an AWS account
- We will require an aws acccount with root access. I was provided one while doing this project at the end of my intensive course at aicore.

## Milestone 2: Getting started
##### Task 1: Download the pintrest infrastructure
- Run the: `user_posting_emulation.py` file which contains three tables.
- Create a separate yaml file for storing the credentials.
- Add the yaml file extension to the .gitignore to prevent git from tracking it.
##### Task 2: Signing in to the AWS console
##### Step 1:
- Navigate to https://aws.amazon.com/ to sign in to the AWS Console.
##### Step 2: To login we will need the following credentials:
- Account ID
- IAM user name
- Password
> Throughout the project we will be using: `US- east -1 N.virginia` region for the AWS cloud.

## Milestone 3: Batch processing: configure the EC2 kafka client
##### Task 1 : Create a .pem file locally in vscode
##### Step 1:
- In vscode created a keypair file with .pem extension. This file will contain the necessary credentials to connect to the EC2 instance.
- Located the keypair associated with EC2 instance by navigating to the parameter store in AWS using the keypairID provided.
- Select the keypair by ticking the checkbox and click on show decrypted value, Then copy the entire keypair value including BEGING & END header into the .pem file created locally.
- Retrieved the EC2 instance name using the USERID by navigating to the EC2 dashboard and under details copy the "key pair assigned at launch" from the details tab and rename the .pem file with it.
##### Task 2: Estabilishing connection to EC2 client using SSH client
> Once you have located the instance using USERID select it from the tick box and press on connect button. There are various methods to connect we will use SSH connection type for this project.
- We use the terminal to connect by navigating to the .pem directory, setting the necessary permissions to modify it if not viewable by using the command: `chmod 400 <file name>`.
- Run the ssh command: `ssh -i "<keypair.pem>" ec2-user@ec2-3-93-70-12.compute-1.amazonaws.com` in the terminal also shown on the ssh instructions page in the terminal.
- Please ensure that your .pem file is within the same directory as where you are running this command.
- Secondly, ensure that your .pem file is named as correctly.
> If everything ran succesfully you should see "complete!" returned on the terminal.
##### Task 3: Installing kafka on EC2 client machine
##### Step 1: 
- Once inside the EC2 client, install java using the following command: `sudo yum install java-1.8.0`.
- Because the cluster is runnning on 2.12-2.8.1 version we will install the same version of kafka i.e (2.12-2.8.1) on the ec2 instance, otherwise we wouldn't be able to communicate with the MSK cluster.
- Download kafka using command: `wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz`.
- Unzip the file using: `tar -xzf kafka_2.12-2.8.1.tgz`.
##### Step 2: Installing AWS IAM authentication package
- To send messages to a topic or create topics on the MSK cluster, the client needs to be authenticated, as we know MSK uses IAM to authenticate and authorize requests from client.
- The aws account I am working with already has a preconfigured IAM authenticated MSK cluster, so i wont be creating one.
- Installed the IAM MSK authentication package by navigating to the: `Kafka_2.12-.8.1/libs` directory. Inside here i have downloaded the IAM MSK authentication package from Github, using the following command
`wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar`
- This package is necessary to connect to MSK clusters that require IAM authentication.
- Once downloaded, a file named: `aws-msk-iam-auth-1.1.5-all.jar` will be shown inside the libs directory.
- Created `CLASSPATH` variable to store the location of the aws jar file so that it can be accessed from any directory.
- Save the following command `export CLASSPATH=/home/ec2-user/kafka_2.12-2.8.1/libs/aws-msk-iam-auth-1.1.5-all.jar` inside the: `nano ~/.bashrc` file.
- Once saved run: `source ~/.bashrc`.
> To verify the path is set run: `echo $CLASSPATH` it should return the location of the jar file.
##### Step 3: Configure kafka to use AWS IAM service
- IAM Role for EC2 was already configured for me, otherwise we should create an EC2 Access IAM role.
- From Iam console and roles section selected the role using my USERID, we will copy this role ARN and make a note of it, as we will be using it later for the cluster authentication
- From the Trust relationships tab Edited trust policy by clicking on add principal and selecting IAM roles as principal type.
- Replace the ARN with the EC2 IAM Role we copied from the IAM roles console.
- By following the steps above you will be able to now assume the <UserId>-ec2-access-role, which contains the necessary permissions to authenticate to the MSK cluster.
##### Step 4: Navigate to the Kafka/bin directory and configure the client properties file 
- Create a client.properties file using command:
`nano client.properties`
> The clients configuration file should contain the following:
- `security.protocol = SASL_SSL`
#sets up TLS for encryption and SASL for authN
- `sasl.mechanism = AWS_MSK_IAM`
#identifies the SASL mechanism to use
- `sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="<Your Access Role>/ARN"`
#binds SASL client implementation,
- In the above line make sure to enter the IAM EC2 access role we copied FROM the IAM ROLES section in: "<Your Access Role>/ARN" explicitly.
- `sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler`
#encapsulates constructing a SigV4 signature based on extracted credentials
#the SASL client bound by "sasl.jaas.config" invokes this class_post.
##### Task 4: Creating topics on the Kafka client
- As you know before creating a topic we first need to have information about the cluster Bootstrap server string and the Plaintext Apache Zookeeper connection string.
##### Step 1:
- Go to MSK and select the cluster, and click view client information.
- Make note of the cluster Bootstrap server string[Private endpoint (single-VPC)] and the Plaintext Apache Zookeeper[TLS/Plaintext] connection string.
##### Step 2:
- Created three topics namely, userid.pin, userid.geo, userid.user replacing with my userid explicitly using the following syntax:
`./kafka-topics.sh --bootstrap-server BootstrapServerString --command-config client.properties --create --topic <topic_name> `
- Run the above command inside the kafka/bin folder, Remember to replace the bootstrapserverstring from the cluster information tab while running the above create topic command in the terminal.

## Milestone 4: Connecting MSK cluster to S3 bucket:
##### Task 1 : Create a custom plugin with MSK Connect
##### Step 1: Navigate to the S3 console and find the bucket that contains your `USERID`
- Again, my S3 bucket was preconfigured, you will need to create a bucket manually.
- Make a note of the bucket name, it will have the following format: `user-<your_UserId>-bucket`.
##### Step 2: Download the Confluent.io AMAZON S3 connector
- In EC2 client assume admin user privileges: `sudo -u ec2-user -i`.
- Create directory where we will save our connector: `mkdir kafka-connect-s3 && cd kafka-connect-s3`.
- Download confluent connector using the following code: `Wget https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip`.
- Copy connector to our s3 bucket: `aws s3 cp ./confluentinc-kafka-connect-s3-10.5.13.zip s3://<BUCKET_NAME>/kafka-connect-s3/`.
- Replace the correct version of confluent zip file, at the time of writing this readme file, the correct version is: `10.5.13.zip`.
- Once this is done you can navigate to the s3 bucket and see that connector is uploaded inside the: `kafka-connect-s3/` folder.
##### Step 3: Create a custom plugin
- Now, open the MSK console and select Custom plugins under the MSK Connect section on the left side of the console.
- Choose Create custom plugin.
- Click Browse S3 on the top right of the custom plugin page and find the bucket where you uploaded the Confluent connector ZIP file.
- Then, in the list of objects in that bucket select the ZIP file and select the Choose button. Give the plugin a name and press Create custom plugin.
- Once the plugin has been created you should see the following message at the top of your browser window:
`plugin <PLUGIN_NAME> was successfully created. The custom plugin was created. You can now create a connector using this custom plugin`.
##### Task 2: Create a connector with MSK Connect
- In the MSK console, select Connectors under the MSK Connect section on the left side of the console. 
- Choose Create connector.
- In the list of plugin, select the plugin you have just created, and then click Next. 
- For the connector name choose the desired name, and then choose your MSK cluster from the cluster list.
> In the connector configuration settings copy the following configuration:
- `connector.class=io.confluent.connect.s3.S3SinkConnector`
- `s3.region=us-east-1` #same region as our bucket and cluster
- `flush.size=1`
- `schema.compatibility=NONE`
- `tasks.max=3` #include nomeclature of topic name, given here as an example will read all data from topic names starting with msk.topic....
- `topics.regex=<YOUR_UUID>.*` 
- `format.class=io.confluent.connect.s3.format.json.JsonFormat`
- `partitioner.class=io.confluent.connect.storage.partitioner.DefaultPartitioner`
- `value.converter.schemas.enable=false`
- `value.converter=org.apache.kafka.connect.json.JsonConverter`
- `storage.class=io.confluent.connect.s3.storage.S3Storage`
- `key.converter=org.apache.kafka.connect.storage.StringConverter`
- `s3.bucket.name=<BUCKET_NAME>`
> Make sure to replace the `bucket name` and `UUID` in the topics.regex field explicitly.
> Leave the rest of the configurations as default, except for:
- Connector type change to Provisioned and make sure both the MCU count per worker and Number of workers are set to 1
- Worker Configuration, select Use a custom configuration, then pick confluent-worker
- Access permissions, where you should select the IAM role you have created previously
- Skip the rest of the pages until you get to Create connector button page. 
> Once your connector is up and running you will be able to visualise it in the connectors tab in the MSK console.

## Milestone 5: Batch processing : Configuring an API in API gateway
##### Task 1: Build a Kafka REST proxy integration method for the API
> For this project we will not need to create our own API, as I have been provided with one already. The API name will be the same as UserId.

##### Step 1: Create a resource that allows you to build a PROXY integration for your API.
- Navigate to API GATEWAY and enter the userid, find the preconfigured api and then you will be inside RESOURCES pane
- For Resource Name enter {proxy+} - Proxy integrations provide the selected integration access to many resources and features at once, without specifying multiple resource paths using the greedy parameter. This {proxy+} ensures that we can nest or build upon as many child folders deep inside our root api. Finally, select Enable API Gateway CORS and choose Create Resource.
- After you create the resource, you can start creating methods for this resource. To use a method, you need to 'integrate' it with an endpoint on the backend

##### Step 2: Creating 'HTTP ANY' method
- To set up an integration click on the ANY resource, then on the Edit integration button.
- For Integration type select HTTP. Make sure to also select the 'HTTP proxy integration' toggle.
- For HTTP method select 'ANY'.
- For the Endpoint URL, you will need to enter your Kafka Client Amazon EC2 Instance PublicDNS.
- You can obtain your EC2 Instance Public DNS by navigating to the EC2 console. Here, select your client EC2 machine and look for Public IPv4 DNS and copy this.
- The endpoint URL should have the following format: `http://KafkaClientEC2InstancePublicDNS:8082/{proxy}`.
- In the url replace the: `KafkaClientEC2InstancePublicDNS` explicitly.

##### Step 3: Deploying the API
- To deploy the API use the Deploy API button in the top-right corner of the API page
- For Deployment stage, choose New Stage.
- For Stage name enter the desired stage name(for example dev, test or production). Finally, choose Deploy 
- After Deploying the API make a note of the Invoke URL, as you will need it in a later task.
- Your external URL will look like:
`https://YourAPIInvokeURL/test/`.

##### Task 2: Set up the Kafka REST proxy on the EC2 client
- Now that you have set up the Kafka REST Proxy integration for your API, you need to set up the Kafka REST Proxy on your EC2 client machine.

##### Step 1: Installing the confluent package for the Kafka REST Proxy on your EC2 client machine
- To be able to consume data using MSK from the API we have just created, we will need to download some additional packages on a client EC2 machine, that will be used to communicate with the MSK cluster.
- To install the REST proxy package run the following commands on your EC2 instance:
`sudo wget https://packages.confluent.io/archive/7.2/confluent-7.2.0.tar.gz`
- Unzip the file using:
`tar -xvzf confluent-7.2.0.tar.gz`
- You should now be able to see a confluent-7.2.0 directory on your EC2 instance. 
- To configure the REST proxy to communicate with the pintrest cluster, and to perform IAM authentication you first need to navigate to: `confluent-7.2.0/etc/kafka-rest`. 
- Inside here run the following command to modify the kafka-rest.properties file:
`nano kafka-rest.properties`
- Firstly, you need to modify the bootstrap.servers and the zookeeper.connect variables in this file, with the corresponding Boostrap server string and Plaintext Apache Zookeeper connection string respectively. see: Milestone3 task4 - step1.
- Secondly, to surpass the IAM authentication of the MSK cluster, we will make use of the IAM MSK authentication package again, this package was already downloaded previously. see: Milestone3 task3 - step2.
> Now add the following to the kafka-rest.properties file
- `client.security.protocol = SASL_SSL` #Sets up TLS for encryption and SASL for authN.
- `client.sasl.mechanism = AWS_MSK_IAM` #Identifies the SASL mechanism to use.
- `client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";` #Binds SASL client implementation, encapsulates constructing a SigV4 signature based on extracted credentials.
- `client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler` #The SASL client bound by "sasl.jaas.config" invokes this class.
##### Step 2:
Allow the REST proxy to perform IAM authentication to the MSK cluster by modifying the kafka-rest.properties file.
To configure the REST proxy to communicate with the desired MSK cluster, and to perform IAM authentication you first need to navigate to confluent-7.2.0/etc/kafka-rest.
Inside here run the following command to modify the kafka-rest.properties file:
`nano kafka-rest.properties`
> Add the following to the kafka-rest.properties file: 
- `client.security.protocol = SASL_SSL` #Sets up TLS for encryption and SASL for authN.
- `client.sasl.mechanism = AWS_MSK_IAM` # Identifies the SASL mechanism to use.
- `client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";` #Binds SASL client implementation, encapsulates constructing a SigV4 signature based on extracted credentials.
- `client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler` #The SASL client bound by "sasl.jaas.config" invokes this class.
##### Step 3: Starting the REST proxy on the EC2 client machine














API Repsonses in Python

Now we can use the Python requests library to test the API and obtain a response. To do this, you will have to send POST requests to your Invoke URL with the desired data.
To see whether the request was successfully processed we can print(response.status_code), which should return a status 200, indicating success.


















