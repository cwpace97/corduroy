import json
import pymysql

def lambda_handler(event, context):
    print(f"received event: {event}")
    obj = preprocess_incoming_event(event)

    print("nothing to see here...")

    connection = pymysql.connect(host='your_rds_endpoint',

    user='your_username',
    password='your_password',
    db='your_database_name',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)


    return {
        "statusCode": 200
    }

def preprocess_incoming_event(event):
    sns_message = json.loads(event["Records"][0]["body"])
    object = json.loads(sns_message["Message"])
    return object

def parse_information(obj):
    # message = {
    #     "updatedDate": formatted,
    #     "mountain": "copper",
    #     "lifts": lifts_set,
    #     "runs": runs_set
    # }
    print(obj)