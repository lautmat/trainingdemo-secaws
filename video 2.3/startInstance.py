import json
import boto3

#Setting default values
region="us-east-1"

ec2 = boto3.client("ec2", region_name=region)

def lambda_handler(event, context):

    try:
        if 'instanceid' in event:
            instanceid = event.get('instanceid')
        else:    
            instanceid = json.loads(event['Records'][0]["body"]).get('instanceid')

        StartInstance = ec2.start_instances(
            InstanceIds=[instanceid]          
            )
        return {
            "statusCode": 200,
            "body": json.dumps({"instance": StartInstance['StartingInstances'][0]['InstanceId']})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }