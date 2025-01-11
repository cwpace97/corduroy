import os
import json
import pymysql
import boto3
from botocore.exceptions import ConnectTimeoutError, ClientError
from botocore.config import Config as BotoConfig
import pymysql.cursors

def lambda_handler(event, context):
    print(f"received event: {event}")
    obj = preprocess_incoming_event(event)
    print(obj)

    secret_name = os.environ.get('RDS_CONNECTION_SECRET')
    connection = build_connection_obj(secret_name)

    print("normal query")
    sql = "SELECT CURRENT_USER();"
    resp = execute_sql(connection, sql)
    print(f"RESPONSE: {resp}")

    print("error query")
    sql = "SELECT CURENT_USER();"
    resp = execute_sql(connection, sql)



    return {
        "statusCode": 200
    }

def preprocess_incoming_event(event):
    sns_message = json.loads(event["Records"][0]["body"])
    object = json.loads(sns_message["Message"])
    return object

def parse_information(obj):
    lifts = obj.get("lifts", [])
    runs = obj.get("runs", [])
    location = obj.get("mountain", "No_Location")
    date = obj.get("updatedDate", "1990-01-01")
    # message = {
    #     "updatedDate": formatted,
    #     "mountain": "copper",
    #     "lifts": lifts_set,
    #     "runs": runs_set
    # }

    print(obj)

def get_secret(secret_name):
    print("Gathering secret...")
    region_name = "us-east-1"
    boto_config = BotoConfig(
        connect_timeout = 30, #seconds
        retries = {
            "max_attempts": 1,
            "mode": "standard"
        }
    )

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        config = boto_config
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ConnectTimeoutError as e:
        print("Timed out grabbing secret...")
        raise e
    except Exception as e:
        print('general exception raised')
        raise e
    return get_secret_value_response["SecretString"]

def build_connection_obj(secret_name):
    secret_value = json.loads(get_secret(secret_name))
    print("Connecting to RDS...")
    connection_obj = pymysql.connect(
        host = secret_value.get("host"),
        user = secret_value.get("username"),
        password = secret_value.get("password"),
        db = secret_value.get("dbname"),
        charset = 'utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connected")
    return connection_obj

def execute_sql(connection, sql_statement):
    cursor = connection.cursor()
    resp = cursor.execute(sql_statement)
    print(resp)
    results = cursor.fetchall()
    return results

def select_query(connection, sql_statement):
    cursor = connection.cursor()
    results = []
    cursor.execute(sql_statement) # execute select statement

    columns = cursor.description # with this we will get column names from the table
    for value in cursor.fetchall(): # using fetchall , we are getting multiple records 
        tmp = {}
        for (index, column) in enumerate(value): # we will iterate through each value and get the value for that particular header/column name of the table
            tmp[columns[index][0]] = column

        results.append(tmp)
    print(results)