import json
import boto3
import os

#Setting default values
region="us-east-1"

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))
        
        #Parameters from Lambda test event or API Gateway trigger
        if 'objectname' in event: object_name = event.get('objectname')
        else: object_name = json.loads(event['body']).get('objectname')
        if 's3' in event: s3_bucket = event.get('s3')
        else: s3_bucket = json.loads(event['body']).get('s3')

        
        s3 = boto3.client("s3")
        
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