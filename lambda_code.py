import json
import boto3
import os

sf_client = boto3.client('stepfunctions')

def insert_handler(event, context):
    # Loop through all SQS messages
    for sqs_record in event['Records']:
        try:
            # Parse the S3 event from the SQS message body
            s3_event = json.loads(sqs_record['body'])
            
            # Each S3 event can have multiple records
            for s3_record in s3_event['Records']:
                bucket = s3_record['s3']['bucket']['name']
                key = s3_record['s3']['object']['key']

                print(f"Received file from S3 → Bucket: {bucket}, Key: {key}")

                # Prepare input for Step Function
                input_data = {
                    "bucket": bucket,
                    "key": key
                }

                # Start the Step Function execution
                response = sf_client.start_execution(
                    stateMachineArn=os.environ['SRM'],  # pass Step Function ARN as env variable
                    input=json.dumps(input_data)
                )

                print("Step Function execution started:", response['executionArn'])

        except Exception as e:
            print("Error processing SQS record:", e)
            continue

    return {
        "statusCode": 200,
        "body": json.dumps("Step Function triggered successfully from SQS → S3 event")
    }
