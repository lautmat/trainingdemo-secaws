import json
import boto3

#Setting default values
region="us-east-1"

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))
        
        #Parameters from Lambda test event, SQS queue or API Gateway trigger
        if 'instanceid' in event: instanceid = event.get('instanceid')
        elif 'Records' in event: instanceid = json.loads(event['Records'][0]["body"]).get('instanceid')
        else: instanceid = json.loads(event['body']).get('instanceid')
        
        ec2 = boto3.client("ec2", region_name=region)
                
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