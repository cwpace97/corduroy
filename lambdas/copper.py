from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from tempfile import mkdtemp

import os
import json
import boto3
from datetime import datetime as dt

SNS_CLIENT = boto3.client("sns")
RDS_SNS_TOPIC = os.environ.get("RDS_LAMBDA_TOPIC")

def lambda_handler(event, context):
    try: 
        print("starting...")
        print("gathering environment variables")
        os.environ.get('RDS_LAMBDA_TOPIC', None)
        

        # set up driver
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-path=/tmp")
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

        service = Service(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
            service_log_path="/tmp/chromedriver.log"
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        # connect to website
        print("Completed initialization. Connecting to website...")
        copper = "https://www.coppercolorado.com/the-mountain/trail-lift-info/winter-trail-report"
        driver.get(copper)

        print("Driver connected, beginning processing")

        # open lift menus
        for button in driver.find_elements(By.XPATH, '//span[@class="panel-icon"]'):
            button.click()

        print("Menus opened")
        # each row within all the tables
        runs = []
        lifts = []
        rows = driver.find_elements(By.TAG_NAME, "tr")
        for run in rows:
            # print(run.text)
            if isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
                #TODO
                lift_name, lift_status, lift_type = None, None, None
                lift_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                lift_status = isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']")
                lift_type = run.find_element(By.CLASS_NAME, "type").get_attribute("innerHTML")
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)

            else:
                # reset vars
                run_name, run_status, run_difficulty = None, None, None

                run_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                run_status = isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']") 
                try:
                    difficulty_text = run.find_element(By.CLASS_NAME, "difficulty").find_element(By.TAG_NAME, "div").get_attribute("class")
                    if "icon difficulty-level-green" in difficulty_text: run_difficulty = "green"
                    elif "icon difficulty-level-blue" in difficulty_text: run_difficulty = "blue"
                    elif "icon difficulty-level-black-3" in difficulty_text: run_difficulty = "black3"
                    elif "icon difficulty-level-black-2" in difficulty_text: run_difficulty = "black2"
                    elif "icon difficulty-level-black" in difficulty_text: run_difficulty = "black1"
                    
                except NoSuchElementException as e:
                    print("unable to find difficulty")
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                }
                runs.append(run_obj)
        
        # outside
        driver.quit()
        print(lifts)
        print(runs)

        # prep for export/update
        lifts_set = {each['liftName'] : each for each in lifts}.values()
        runs_set = {each['runName'] : each for each in runs}.values()
        now = dt.today()
        formatted = now.strftime("%Y-%m-%d")
        message = {
            "updatedDate": formatted,
            "location": "copper",
            "lifts": list(lifts_set),
            "runs": list(runs_set)
        }
        print(message)
        json_string = json.dumps(message)

        resp = SNS_CLIENT.publish(TopicArn=RDS_SNS_TOPIC, Message=json_string)
        print("Message published")
        print(resp)
    except Exception as e:
        print("generic exception received, returning 202")
        print(e)
        return {
            "statusCode": 202,
            "body": "Exception raised, returning 202"
        } 
    finally:
        return {
            "statusCode": 200,
            "body": "Function executed successfully"
        }

def isElementPresent(driver, lookupType, locatorKey):
    try:
        driver.find_element(lookupType, locatorKey)
        return True
    except NoSuchElementException as e:
        return False

def safeSearch(driver, lookupType, locatorKey):
    try:
        element = driver.find_element(lookupType, locatorKey)
        return element
    except NoSuchElementException as e:
        return None

if __name__ == "__main__":
    lambda_handler("event","context")