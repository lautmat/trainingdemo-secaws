import json
import boto3
import os

#Setting default values
region="us-east-1"

s3 = boto3.client("s3")

def lambda_handler(event, context):

    try:
        object_name = event.get('objectname')
        s3_bucket = event.get('s3')
        
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