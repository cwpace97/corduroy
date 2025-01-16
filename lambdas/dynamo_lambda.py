import os
import re
import json
import boto3
import logging
from botocore.exceptions import ConnectTimeoutError, ClientError
from botocore.config import Config as BotoConfig

secret_name = os.environ.get("RDS_CONNECTION_SECRET")
runs_table = os.environ.get("RUNS_TABLE")
lifts_table = os.environ.get("LIFTS_TABLE")

logging.root.setLevel("INFO")
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        logger.info(f"received event: {event}")
        obj, topic = preprocess_incoming_event(event)
        
        lifts = obj.get("lifts", [])
        runs = obj.get("runs", [])
        location = obj.get("location", "No_Location")
        date = obj.get("updatedDate", "1990-01-01")

        dynamodb = boto3.resource("dynamodb")

        # handle lifts
        resp = update_lifts(dynamodb, lifts, location, date)
        logger.info(resp)

        # handle runs
        resp = update_runs(dynamodb, runs, location, date)
        logger.info(resp)


    except Exception as e:
        logger.info("generic exception received, returning 202")
        logger.error(e)
        return {
            "statusCode": 202,
            "body": "Exception raised, returning 202 to remove message from SQS queue..."
        } 
    finally:
        return {
            "statusCode": 200,
            "body": "Function executed successfully"
        }

def update_lifts(dynamodb, lifts, location, date):
    logger.info("Updating lifts table...")
    for lift in lifts:
        lift['date-location-lift'] = f"{date}-{location}-{lift['liftName']}"
        lift['location'] = location
        lift['updatedDate'] = date
        lift['liftStatus'] = f"{lift['liftStatus']}"
    return dynamo_batch_write_items(dynamodb, lifts_table, lifts)

def update_runs(dynamodb, runs, location, date):
    logger.info("Updating runs table...")
    for run in runs:
        run['date-location-run'] = f"{date}-{location}-{run['runName']}"
        run['location'] = location
        run['updatedDate'] = date
        run['runStatus'] = f"{run['runStatus']}"
    return dynamo_batch_write_items(dynamodb, runs_table, runs)
    

def preprocess_incoming_event(event):
    sns_message = json.loads(event["Records"][0]["body"])
    topic_arn = sns_message.get("TopicArn")
    pattern = "(?!.*:)(.*)$"
    topic = re.search(pattern, topic_arn).group()
    object = json.loads(sns_message["Message"])
    return object, topic

# DYNAMO HELPERS
def convert_dict_to_dynamo_dict(dictionary):
    dynamo_dict = {}
    for key, value in dictionary.items():
        if value is None:
            dynamo_dict[key] = {"NULL": True}
            continue
        if isinstance(value, str):
            dynamo_dict[key] = {"S": value}
        elif isinstance(value, bool): #TODO
            dynamo_dict[key] = {"S": f'{value}'}
        elif isinstance(value, int):
            dynamo_dict[key] = {"N": value}
        else:
            dynamo_dict[key] = {"NULL": True}
    return dynamo_dict
        
def dynamo_batch_write_items(dynamodb, table_name, input_array):
    table = dynamodb.Table(table_name)
    try:
        with table.batch_writer() as writer:
            for item in input_array:
                writer.put_item(Item=item)
        logger.info(f"Successfully wrote {len(input_array)} items into {table_name}.")
        return True
    except ClientError as err:
        logger.info(
            "Couldn't load data into table %s. Here's why: %s: %s",
            table.name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )