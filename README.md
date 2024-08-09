# AWS PINTREST PIPELINE
> The main motivation behind building this project comes from the idea of pintrest utilising the AWS Cloud to crunch billions of data points everyday to decide how to provide value to its cutomers. 
> This project aims at emulating a similar system using the AWS Cloud.

# MILESTONE 1: SETTING UP THE ENVIRONMENT
## TASK 1: CREATE A REMOTE REPOSITORY AND CLONE IT.
> To clone this repository type the command git clone

## TASK 2: SET UP AWS CLOUD ACCOUNT
> We will require an aws acccount with root access.

# MILESTONE 2: GETTING STARTED
## TASK 1: Downloaded the pintrest infrastructure
- Run the "user_posting_emulation.py" file which contains three tables
- Create a separate db_creds.yaml file for storing the credentials.
> Add the yaml file to .gitignore 

## TASK 2: Signing in to the AWS CONSOLE
### STEP 1:
> Navigate to https://aws.amazon.com/  to sign in to the AWS Console.
### STEP 2:
> To login we will need the following credentials:
- Account ID
- IAM user name
- Password
> Throughout the project we will be using US- east -1 N.virginia region for the AWS cloud.

# MILESTONE 3: BATCH PROCESSING: CONFIGURE THE EC2 KAFKA CLIENT
## TASK 1 : CREATE A .PEM FILE LOCALLY
### STEP 1:
- In vscode created a keypair file with .pem extension. This file will contain the necessary credentials to connect to the EC2 instance.
- Located the keypair associated with EC2 instance by navigating to the parameter store in AWS using the keypairID provided.
- Select the keypair by ticking the checkbox and click on show decrypted value, Then copy the entire keypair value including BEGING & END header into the .pem file created locally.
- Retrieved the EC2 instance name using the USERID by navigating to the EC2 dashboard and under details copy the "key pair assigned at launch" from the details tab and rename the .pem file with it.

## TASK 2: ESTABILISHING CONNECTION TO EC2 USING SSH CLIENT
- Once you have located the instance using USERID select it from the tick box and press on connect button. There are various methods to connect we will use SSH connection type for this project.
- We use the terminal to connect by navigating to the .pem directory, setting the necessary permissions to modify it if not viewable by using the command `chmod 400 <file name>`.
- Run the ssh command `ssh -i "<keypair.pem>" ec2-user@ec2-3-93-70-12.compute-1.amazonaws.com` in the terminal also shown on the ssh instructions page in the terminal.
- Please ensure that your .pem file is within the same directory as where you are running this command.
- Secondly, ensure that your .pem file is named as correctly.
> If everything ran succesfully you should see the "complete!" returned on the terminal.

## TASK 3: INSTALLING KAFKA ON EC2 CLIENT MACHINE
### STEP 1 : 
> Once inside the EC2 client, install java using the following command
`sudo yum install java-1.8.0`
- Because the cluster is runnning on 2.12-2.8.1 version we will install the same version of kafka i.e (2.12-2.8.1) on the ec2 instance, otherwise we wouldn't be able to communicate with the MSK cluster.
- `wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz`
- `tar -xzf kafka_2.12-2.8.1.tgz`
### STEP 2: INSTALLING AWS IAM AUTHENTICATION PACKAGE ON EC2 CLIENT
- To send messages to a topic or create topics on the MSK cluster, the client needs to be authenticated, as we know MSK uses IAM to authenticate and authorize requests from client.
- The aws account I am working with already has a preconfigured IAM authenticated MSK cluster, so i wont be creating one.
- Installed the IAM MSK authentication package by navigating to the `Kafka_2.12-.8.1/libs` directory. Inside here i have downloaded the IAM MSK authentication package from Github, using the following command
`wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar`
- This package is necessary to connect to MSK clusters that require IAM authentication.
- Once downloaded, a file named `aws-msk-iam-auth-1.1.5-all.jar` will be shown inside the libs directory.
- Created CLASSPATH variable to store the location of the aws jar file so that it can be accessed from any directory using the command 
- Save this command inside the `nano ~/.zshrc` file:
`export CLASSPATH=/home/ec2-user/kafka_2.12-2.8.1/libs/aws-msk-iam-auth-1.1.5-all.jar` 
- Once saved run `source ~/.zshrc`
> To verify the path is set run `echo $CLASSPATH` it should return the location of the jar file.
### STEP 3: CONFIGURE KAFKA TO USE AWS IAM SERVICE
- From Iam console and roles section selected the role using USERID, we will copy this role ARN and make a note of it, as we will be using it later for the cluster authentication
- From the Trust relationships tab Edited trust policy by clicking on add principal and selecting IAM roles as principal type.
- Replace the ARN with the ARN we copied from the IAM roles console.
> By following the steps above you will be able to now assume the <UserId>-ec2-access-role, which contains the necessary permissions to authenticate to the MSK cluster.
### STEP 4: NAVIGATE TO KAFKA/BIN DIRECTORY AND CONFIGURE CLIENT PROPERTIES FILE
> Create a client.properties file
`nano client.properties` 
> The clients configuration file should contain the following:
- #Sets up TLS for encryption and SASL for authN.
`security.protocol = SASL_SSL`
- #Identifies the SASL mechanism to use.
`sasl.mechanism = AWS_MSK_IAM`
- #Binds SASL client implementation.
`sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="<Your Access Role>/ARN"`
- #Encapsulates constructing a SigV4 signature based on extracted credentials.
- #The SASL client bound by "sasl.jaas.config" invokes this class.
`sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler`
> Make sure to enter the EC2 access role we copied form the IAM ROLES in "<Your Access Role>".
## TASK 4: CREATING TOPICS ON KAFKA CLIENT MACHINE
> As you know before creating a topic we first need to have information about the cluster Bootstrap server string and the Plaintext Apache Zookeeper connection string.
### STEP 1:
- Go to MSK and select the cluster, and click view client information.
> Make note of the cluster Bootstrap server string and the Plaintext Apache Zookeeper connection string.
### STEP 2:
> Created three topics namely, userid.pin, userid.geo, userid.user replacing with my userid explicitly.
- Using the following syntax:
`./kafka-topics.sh --bootstrap-server BootstrapServerString --command-config client.properties --create --topic <topic_name> `
> Remember to replace the bootstrapserverstring from the cluster information tab while running the create topic command in the terminal.

# MILESTONE 4: CONNECTING MSK CLUSTER TO A S3 BUCKET:
## TASK 1 : CREATE A CUSTOM PLUGIN WITH MSK CONNECT
### STEP 1:
> Navigate to the S3 console and find the bucket that contains your USERID
- Make a note of the bucket name, it will have the following format
`user-<your_UserId>-bucket`
### STEP 2: DOWNLOAD THE CONFLUENT.IO AMAZON S3 CONNECTOR
> On the EC2 client download the `Confluent.io Amazon S3 Connector` and copy it to the S3 bucket you have identified in the previous step.
- #In EC2 assume admin user privileges
`sudo -u ec2-user -i`
- #Create directory where we will save our connector 
`mkdir kafka-connect-s3 && cd kafka-connect-s3`
- #Download confluent connector using the following code:
`Wget https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip`
- #Copy connector to our s3 bucket 
`aws s3 cp ./confluentinc-kafka-connect-s3-10.5.13.zip s3://<BUCKET_NAME>/kafka-connect-s3/`
> Replace the correct version of confluent zip file, at the time of writing this readme file, the correct version is 10.5.13.zip.
> Once this is done you can navigate to the s3 bucket and see that connector is uploaded inside the kafka-connect-s3/ folder.
### STEP 3: CREATE A CUSTOM PLUGIN
> Now, open the MSK console and select Custom plugins under the MSK Connect section on the left side of the console.
- Choose Create custom plugin.
- Click Browse S3 on the top right of the custom plugin page and find the bucket where you upload the Confluent connector ZIP file.
- Then, in the list of objects in that bucket select the ZIP file and select the Choose button. Give the plugin a name and press Create custom plugin.
> Once the plugin has been created you should see the following message at the top of your browser window:
`plugin <PLUGIN_NAME> was successfully created. The custom plugin was created. You can now create a connector using this custom plugin`
## TASK 2: CREATE A CONNECTOR WITH MSK CONNECT
> In the MSK console, select Connectors under the MSK Connect section on the left side of the console. 
- Choose Create connector.
- In the list of plugin, select the plugin you have just created, and then click Next. 
- For the connector name choose the desired name, and then choose your MSK cluster from the cluster list.
- In the Connector configuration settings copy the following configuration:
`
connector.class=io.confluent.connect.s3.S3SinkConnector
# same region as our bucket and cluster
s3.region=us-east-1
flush.size=1
schema.compatibility=NONE
tasks.max=3
# include nomeclature of topic name, given here as an example will read all data from topic names starting with msk.topic....
topics.regex=<YOUR_UUID>.*
format.class=io.confluent.connect.s3.format.json.JsonFormat
partitioner.class=io.confluent.connect.storage.partitioner.DefaultPartitioner
value.converter.schemas.enable=false
value.converter=org.apache.kafka.connect.json.JsonConverter
storage.class=io.confluent.connect.s3.storage.S3Storage
key.converter=org.apache.kafka.connect.storage.StringConverter
s3.bucket.name=<BUCKET_NAME>
`
> Make sure to replace the bucket name and UUID in the topics.regex field explicitly.
> Leave the rest of the configurations as default, except for:
- Connector type change to Provisioned and make sure both the MCU count per worker and Number of workers are set to 1
- Worker Configuration, select Use a custom configuration, then pick confluent-worker
- Access permissions, where you should select the IAM role you have created previously
- Skip the rest of the pages until you get to Create connector button page. 
> Once your connector is up and running you will be able to visualise it in the Connectors tab in the MSK console.

# MILESTONE 5: BATCH PROCESSING : CONFIGURING AN API IN API GATEWAY
## TASK 1: BUILD A KAFKA REST PROXY INTEGRATION METHOD FOR THE API
> For this project we will not need to create our own API, as I have been provided with one already. The API name will be the same as UserId.
### Step 1:
> Create a resource that allows you to build a PROXY integration for your API.
### Step 2:
> For the previously created resource, create a HTTP ANY method. When setting up the Endpoint URL, make sure to copy the correct PublicDNS, from the EC2 machine you have been working on in the previous milestones.
- Remember, this EC2 should have the same name as your UserId.
### Step 3:
> Deploy the API and make a note of the Invoke URL, as you will need it in a later task.


## TASK 2: SET UP THE KAFKA REST PROXY ON THE EC2 CLIENT
> Now that you have set up the Kafka REST Proxy integration for your API, you need to set up the Kafka REST Proxy on your EC2 client machine.
### Step 1:
> First, install the Confluent package for the Kafka REST Proxy on your EC2 client machine.
### Step 2:
> Allow the REST proxy to perform IAM authentication to the MSK cluster by modifying the kafka-rest.properties file.
### Step 3:
> Start the REST proxy on the EC2 client machine.

















