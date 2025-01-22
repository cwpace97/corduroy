import os
import re
import json
import boto3
import logging
import pymysql
from botocore.exceptions import ConnectTimeoutError, ClientError
from botocore.config import Config as BotoConfig

# secret_name = os.environ.get("RDS_CONNECTION_SECRET")
runs_table = os.environ.get("RUNS_TABLE")
lifts_table = os.environ.get("LIFTS_TABLE")
ski_db = os.environ.get("DB")

logging.root.setLevel("INFO")
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        logger.info(f"received event: {event}")
        obj, topic = preprocess_incoming_event(event)
        connection = build_connection_obj(ski_db)
        
        lifts = obj.get("lifts", [])
        runs = obj.get("runs", [])
        location = obj.get("location", "No_Location")
        date = obj.get("updatedDate", "1990-01-01")


        # handle lifts
        resp = update_lifts(connection, lifts, location, date)
        logger.info(resp)

        # handle runs
        resp = update_runs(connection, runs, location, date)
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

def update_lifts(connection, lifts, location, date):
    print("Updating lifts table")
    sql = f"""
        INSERT INTO {ski_db}.{lifts_table} (location, lift_name, lift_type, lift_status, updated_date)
        VALUES """
    vals = ""
    for lift in lifts:
        txt = '("%s", "%s", "%s", %s, "%s"),' % (
            location, 
            lift.get("liftName", "N/A"), 
            lift.get("liftType", "N/A"),
            lift.get("liftStatus", False), 
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
            run.get("runName", "N/A"), 
            run.get("runDifficulty", "N/A"),
            run.get("runStatus", False), 
            date)
        vals += txt
    vals = vals[:-1]+";"
    sql += vals
    print(sql)
    resp = execute_sql(connection, sql)
    return resp
    
def execute_sql(connection, sql_statement):
    cursor = connection.cursor()
    resp = cursor.execute(sql_statement)
    print(f"{resp} rows affected")
    results = cursor.fetchall()
    connection.commit()
    return results

def preprocess_incoming_event(event):
    sns_message = json.loads(event["Records"][0]["body"])
    topic_arn = sns_message.get("TopicArn")
    pattern = "(?!.*:)(.*)$"
    topic = re.search(pattern, topic_arn).group()
    object = json.loads(sns_message["Message"])
    return object, topic

def build_connection_obj(db):
    host_name = os.environ.get("HOST")
    user_name = os.environ.get("USER")
    pwd = os.environ.get("PASSWORD")
    connection_obj = pymysql.connect(
        host = host_name,
        user = user_name,
        password = pwd,
        db = db,
        charset = "utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    logger.info("Connected")
    return connection_obj