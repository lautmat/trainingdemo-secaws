import json
import boto3
import os

#Setting default values
region="us-east-1"
owner="default"

def lambda_handler(event, context):

    try:
        print("Event received from Lambda's trigger " + str(event))
        
        global owner
        
        #Parameters from Lambda test event or API Gateway trigger
        if 'keyname' in event: keypair_name = event.get('keyname')
        else: keypair_name = json.loads(event['body']).get('keyname')
        if 's3' in event: s3_bucket = event.get('s3')
        else: s3_bucket = json.loads(event['body']).get('s3')
        if 'owner' in event: owner = event.get('owner')
        elif 'body' in event: owner = json.loads(event['body']).get('owner')
        
        ec2 = boto3.client("ec2", region_name=region)
        
        s3 = boto3.client("s3")

        key_pair = ec2.create_key_pair(KeyName=keypair_name,TagSpecifications=[{'ResourceType':'key-pair','Tags':[{'Key':'Owner','Value':owner},]},])
        private_key = key_pair["KeyMaterial"]
        file_name = '/tmp/' + keypair_name +'.pem'
        with os.fdopen(os.open(file_name, os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
            handle.write(private_key)
        upload = s3.upload_file(file_name, s3_bucket, keypair_name)
        tag = s3.put_object_tagging(Bucket=s3_bucket,Key=keypair_name,Tagging={'TagSet':[{'Key':'Owner','Value':owner},]},)
        return {
            "statusCode": 200,
            "body": json.dumps("Key uploaded")
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }