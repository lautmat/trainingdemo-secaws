import json
import boto3

#Setting default values
region="us-east-1"
owner="default"

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))
        
        global owner
                
        #Parameters from Lambda test event or API Gateway trigger
        if 'owner' in event: owner = event.get('owner')
        elif 'body' in event: owner = json.loads(event['body']).get('owner')        
        
        ec2 = boto3.client("ec2", region_name=region)
        
        instances = [ ]
        GetInstance = ec2.describe_instances(Filters=[
            {
                "Name": "tag:LaunchedBy",
                "Values": ["SIMS"],
            },
            {
                "Name": "tag:Owner",
                "Values": [owner],
            }
        ]).get("Reservations")
        for reservation in GetInstance:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
            instances.append(instance_id)
        return {
            "statusCode": 200,
            "body": json.dumps(instances)
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }