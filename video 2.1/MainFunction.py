import json
import boto3

#Setting default values
region="us-east-1"

lambda_inv = boto3.client("lambda", region_name=region)

def lambda_handler(event, context):

    try:
        child_function = event.get('childfunction')

        payload = {
            "message":"Hi From FunctionA", 
            "request": "say_hello"
        }
        response = lambda_inv.invoke(FunctionName=child_function,InvocationType='RequestResponse',Payload=json.dumps(payload))

        return {
            "statusCode": 200,
            "body": json.dumps({"ResponseChildFunction": response["Payload"].read().decode()})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
