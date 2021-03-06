import json
import boto3

#Setting default values
region="us-east-1"
ec2_min=1
ec2_max=1
queuename="SIMSqueue1"
ec2_ami_id="ami-0ed9277fb7eb570c9"
ec2_type="t2.micro"
owner="default"

def lambda_handler(event, context):
    
    try:
        print("Event received from Lambda's trigger " + str(event))
        
        global ec2_ami_id, ec2_type, owner
            
        #Parameters from Lambda test event or API Gateway trigger
        if 'ami' in event: ec2_ami_id = event.get('ami')
        if 'type' in event: ec2_type = event.get('type')
        if 'owner' in event: owner = event.get('owner')
        if 'body' in event: 
            ec2_ami_id = json.loads(event['body']).get('ami')
            ec2_type = json.loads(event['body']).get('type')
            owner = json.loads(event['body']).get('owner')
        
        ec2 = boto3.client("ec2", region_name=region)
        
        sqs = boto3.resource('sqs')
        
        RunInstance = ec2.run_instances(
            ImageId=ec2_ami_id,
            InstanceType=ec2_type,
            MinCount=ec2_min,
            MaxCount=ec2_max,
            TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'LaunchedBy',
                        'Value': 'SIMS'
                    },
                    {
                        'Key': 'Owner',
                        'Value': owner
                    },                    
                ]
            },
            ]            
            )
        
        queue = sqs.get_queue_by_name(QueueName=queuename)
        SendToQueue = queue.send_message(MessageBody=json.dumps({"instanceid": RunInstance['Instances'][0]['InstanceId']}))
        
        return {
            "statusCode": 200,
            "body": json.dumps({"instanceid": RunInstance['Instances'][0]['InstanceId']})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }