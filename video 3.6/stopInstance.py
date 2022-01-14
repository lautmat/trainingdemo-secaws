import json
import boto3
import os
import hashlib
import hmac
import base64

#Setting default values
region="us-east-1"

IDENTITY_POOL_ID = 'IDENTITY_POOL_ID'
PROVIDER = 'PROVIDER'

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))

        #Parameters from Lambda test event or API Gateway trigger 
        if 'instanceid' in event: instanceid = event.get('instanceid')
        elif 'Records' in event: instanceid = json.loads(event['Records'][0]["body"]).get('instanceid')
        else: instanceid = json.loads(event['body']).get('instanceid')

        if 'id_token' in event: id_token = event.get('id_token')
        elif 'Records' in event: id_token = json.loads(event['Records'][0]["body"]).get('id_token')
        else: id_token = (event['headers']).get('id_token')
        
        identity_client = boto3.client('cognito-identity')
        identity_response = identity_client.get_id(IdentityPoolId=IDENTITY_POOL_ID,Logins={PROVIDER: id_token})
        identity_id = identity_response['IdentityId']
        response = identity_client.get_credentials_for_identity(IdentityId=identity_id,Logins={PROVIDER: id_token})
        
        ec2 = boto3.client("ec2", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
            region_name=region)
            
        StopInstance = ec2.stop_instances(
            InstanceIds=[instanceid]          
            )
        return {
            "statusCode": 200,
            "body": json.dumps({"instance": StopInstance['StoppingInstances'][0]['InstanceId']})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }