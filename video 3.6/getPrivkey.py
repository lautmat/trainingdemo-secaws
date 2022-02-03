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
        if 'objectname' in event: object_name = event.get('objectname')
        else: object_name = json.loads(event['body']).get('objectname')
        if 's3' in event: s3_bucket = event.get('s3')
        else: s3_bucket = json.loads(event['body']).get('s3')

        if 'id_token' in event: id_token = event.get('id_token')
        else: id_token = (event['headers']).get('id_token')

        identity_client = boto3.client('cognito-identity')
        identity_response = identity_client.get_id(IdentityPoolId=IDENTITY_POOL_ID,Logins={PROVIDER: id_token})
        identity_id = identity_response['IdentityId']
        response = identity_client.get_credentials_for_identity(IdentityId=identity_id,Logins={PROVIDER: id_token})
        
        s3 = boto3.client("s3", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"])             
        response = s3.get_object(Bucket=s3_bucket, Key=object_name)
        
        return {
            "statusCode": 200,
            "body": json.dumps(response["Body"].read().decode())
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }