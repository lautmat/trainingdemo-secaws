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

        if 'id_token' in event: id_token = event.get('id_token')
        else: id_token = (event['headers']).get('id_token')
        
        #Decode Cognito username from JWT id_token
        username = jwt.get_unverified_claims(id_token).get('cognito:username')

        identity_client = boto3.client('cognito-identity')
        identity_response = identity_client.get_id(IdentityPoolId=IDENTITY_POOL_ID,Logins={PROVIDER: id_token})
        identity_id = identity_response['IdentityId']
        response = identity_client.get_credentials_for_identity(IdentityId=identity_id,Logins={PROVIDER: id_token})
        
        kms = boto3.client("kms", aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
            region_name=region)   
        
        #Create KMS key with user id as Owner's tag value
        createkey = kms.create_key(
            Tags=[{
                    'TagKey': 'Owner',
                    'TagValue': identity_id,
                },],)
        
        keyid = createkey["KeyMetadata"].get('Arn')
        
        #Use username as alia for the key
        createalias = kms.create_alias(AliasName='alias/'+username,TargetKeyId=keyid,)
        
        return {
            "statusCode": 200,
            "body": json.dumps("KMS key " + keyid + " with the alias " + username + " created")
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }