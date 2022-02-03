import json
import boto3
import os
import hashlib
import hmac
import base64

import ecdsa as ecdsa
from jose import jwt

#Setting default values
region="us-east-1"

IDENTITY_POOL_ID = 'IDENTITY_POOL_ID'
PROVIDER = 'PROVIDER'

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))

        #Parameters from Lambda test event or API Gateway trigger        
        if 'keyname' in event: keypair_name = event.get('keyname')
        else: keypair_name = json.loads(event['body']).get('keyname')
        if 's3' in event: s3_bucket = event.get('s3')
        else: s3_bucket = json.loads(event['body']).get('s3')

        if 'id_token' in event: id_token = event.get('id_token')
        else: id_token = (event['headers']).get('id_token')
        
        #Decode Cognito username from JWT id_token
        username = jwt.get_unverified_claims(id_token).get('cognito:username')

        identity_client = boto3.client('cognito-identity')
        identity_response = identity_client.get_id(IdentityPoolId=IDENTITY_POOL_ID,Logins={PROVIDER: id_token})
        identity_id = identity_response['IdentityId']
        response = identity_client.get_credentials_for_identity(IdentityId=identity_id,Logins={PROVIDER: id_token})
        
        ec2 = boto3.client("ec2", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
            region_name=region)        
        
        s3 = boto3.client("s3", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"])             
        
        key_pair = ec2.create_key_pair(KeyName=keypair_name,TagSpecifications=[{'ResourceType':'key-pair','Tags':[{'Key':'Owner','Value':identity_id},]},])
        private_key = key_pair["KeyMaterial"]
        file_name = '/tmp/' + keypair_name +'.pem'
        with os.fdopen(os.open(file_name, os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
            handle.write(private_key)
        upload = s3.upload_file(file_name, s3_bucket, keypair_name,
                     ExtraArgs={'ServerSideEncryption':'aws:kms','SSEKMSKeyId':'alias/'+username})
        tag = s3.put_object_tagging(Bucket=s3_bucket,Key=keypair_name,Tagging={'TagSet':[{'Key':'Owner','Value':identity_id},]},)
        return {
            "statusCode": 200,
            "body": json.dumps("Key uploaded")
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }