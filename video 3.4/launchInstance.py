import json
import boto3
import os
import hashlib
import hmac
import base64

#Setting default values
region="us-east-1"
ec2_min=1
ec2_max=1
queuename="SIMSqueue1"
ec2_ami_id="ami-0ed9277fb7eb570c9"
ec2_type="t2.micro"

IDENTITY_POOL_ID = 'IDENTITY_POOL_ID'
PROVIDER = 'PROVIDER'

def lambda_handler(event, context):
    
    try:
        print("Event received from Lambda's trigger " + str(event))

        global ec2_ami_id, ec2_type

        #Parameters from Lambda test event or API Gateway trigger
        if 'ami' in event: ec2_ami_id = event.get('ami')
        if 'type' in event: ec2_type = event.get('type')

        if 'id_token' in event: id_token = event.get('id_token')
        else: id_token = (event['headers']).get('id_token')

        identity_client = boto3.client('cognito-identity')
        identity_response = identity_client.get_id(IdentityPoolId=IDENTITY_POOL_ID,Logins={PROVIDER: id_token})
        identity_id = identity_response['IdentityId']
        response = identity_client.get_credentials_for_identity(IdentityId=identity_id,Logins={PROVIDER: id_token})
        
        ec2 = boto3.client("ec2", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
            region_name=region)
        
        RunInstance = ec2.run_instances(
            ImageId=ec2_ami_id,
            InstanceType=ec2_type,
            MinCount=ec2_min,
            MaxCount=ec2_max,
            TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'LaunchedBy',
                        'Value': 'SIMS'
                    },
                    {
                        'Key': 'Owner',
                        'Value': identity_id
                    },                    
                ]
            },
            ]            
            )
        
        sqs = boto3.resource('sqs')
        
        queue = sqs.get_queue_by_name(QueueName=queuename)
        SendToQueue = queue.send_message(MessageBody=json.dumps({"instanceid": RunInstance['Instances'][0]['InstanceId']}))
        
        return {
            "statusCode": 200,
            "body": json.dumps({"instanceid": RunInstance['Instances'][0]['InstanceId']})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }