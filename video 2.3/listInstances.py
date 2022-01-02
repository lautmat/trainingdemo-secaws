import json
import boto3

#Setting default values
region="us-east-1"
owner="default"

ec2 = boto3.client("ec2", region_name=region)

def lambda_handler(event, context):

    global owner
    if 'owner' in event: owner = event.get('owner')

    try:
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
                print(f"{instance_id}")
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