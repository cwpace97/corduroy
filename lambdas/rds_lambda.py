import os
import re
import json
import pymysql
import boto3
from botocore.exceptions import ConnectTimeoutError, ClientError
from botocore.config import Config as BotoConfig
import pymysql.cursors

secret_name = os.environ.get("RDS_CONNECTION_SECRET")
ski_db = os.environ.get("SKI_DATABASE")
runs_table = os.environ.get("RUNS_TABLE")
lifts_table = os.environ.get("LIFTS_TABLE")

def lambda_handler(event, context):
    try:
        print(f"received event: {event}")
        obj, topic = preprocess_incoming_event(event)
        connection = build_connection_obj(secret_name)
        
        lifts = obj.get("lifts", [])
        runs = obj.get("runs", [])
        location = obj.get("location", "No_Location")
        date = obj.get("updatedDate", "1990-01-01")

        # handle lifts
        resp = update_lifts(connection, lifts, location, date)
        print(resp)

        # handle runs
        resp = update_runs(connection, runs, location, date)
        print(resp)


    except Exception as e:
        print("generic exception received, returning 202")
        print(e)
        return {
            "statusCode": 202,
            "body": "Exception raised, returning 202 to remove message from SQS queue..."
        } 
    finally:
        return {
            "statusCode": 200,
            "body": "Function executed successfully"
        }

def update_lifts(connection, lifts, location, date):
    print("Updating lifts table")
    sql = f"""
        INSERT INTO {ski_db}.{lifts_table} (location, lift_name, lift_type, lift_status, updated_date)
        VALUES """
    vals = ""

    for lift in lifts:
        txt = '("%s", "%s", "%s", %s, "%s"),' % (
            location, 
            lift.get("Lift_Name", "N/A"), 
            lift.get("Lift_Type", "N/A"),
            lift.get("Lift_Status", False), 
            date)
        vals += txt
    vals = vals[:-1]+";"
    sql += vals

    resp = execute_sql(connection, sql)
    return resp

def update_runs(connection, runs, location, date):
    print("Updating runs table")
    sql = f"""
        INSERT INTO {ski_db}.{runs_table} (location, run_name, run_difficulty, run_status, updated_date)
        VALUES """
    vals = ""

    for run in runs:
        txt = '("%s", "%s", "%s", %s, "%s"),' % (
            location, 
            run.get("Run_Name", "N/A"), 
            run.get("Run_Difficulty", "N/A"),
            run.get("Run_Status", False), 
            date)
        vals += txt
    vals = vals[:-1]+";"
    sql += vals
    print(sql)

    resp = execute_sql(connection, sql)
    return resp

def preprocess_incoming_event(event):
    sns_message = json.loads(event["Records"][0]["body"])
    topic_arn = sns_message.get("TopicArn")
    pattern = "(?!.*:)(.*)$"
    topic = re.search(pattern, topic_arn).group()
    object = json.loads(sns_message["Message"])
    return object, topic

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
        service_name="secretsmanager",
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
        print("general exception raised")
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
        charset = "utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connected")
    return connection_obj

def execute_sql(connection, sql_statement):
    cursor = connection.cursor()
    resp = cursor.execute(sql_statement)
    print(f"{resp} rows affected")
    results = cursor.fetchall()
    connection.commit()
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