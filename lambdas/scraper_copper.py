import common
import os
import boto3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions

SNS_CLIENT = boto3.client("sns")
RDS_SNS_TOPIC = os.environ.get("RDS_LAMBDA_TOPIC")
WEBSITE_URL = os.environ.get("WEBSITE_URL")

# set up driver
chrome_options = common.setChromeConfigOptions(ChromeOptions())
chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

service = Service(
    executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
    service_log_path="/tmp/chromedriver.log"
)

DRIVER = webdriver.Chrome(
    service=service,
    options=chrome_options
)

def handler(event, context):
    try: 
        # connect to website
        print("Completed initialization. Connecting to website...")
        DRIVER.get(WEBSITE_URL)
        print("Driver connected, beginning processing")

        # open lift menus
        for button in DRIVER.find_elements(By.XPATH, '//span[@class="panel-icon"]'):
            button.click()

        print("Menus opened")
        # each row within all the tables
        runs = []
        lifts = []
        rows = DRIVER.find_elements(By.TAG_NAME, "tr")
        for run in rows:
            # print(run.text)
            if common.isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
                #TODO
                lift_name = "None"
                lift_status = False
                lift_type = "None"
                
                lift_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                lift_status = common.isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']")
                lift_type = run.find_element(By.CLASS_NAME, "type").get_attribute("innerHTML")
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)

            else:
                # reset vars
                run_name = "None"
                run_status = False
                run_difficulty = "None"

                run_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                run_status = common.isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']") 
                try:
                    difficulty_text = run.find_element(By.CLASS_NAME, "difficulty").find_element(By.TAG_NAME, "div").get_attribute("class")
                    if "icon difficulty-level-green" in difficulty_text: run_difficulty = "green"
                    elif "icon difficulty-level-blue" in difficulty_text: run_difficulty = "blue1"
                    elif "icon difficulty-level-black-3" in difficulty_text: run_difficulty = "black3"
                    elif "icon difficulty-level-black-2" in difficulty_text: run_difficulty = "black2"
                    elif "icon difficulty-level-black" in difficulty_text: run_difficulty = "black1"
                    
                except Exception as e:
                    print("Skipping run")
                    continue
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                }
                runs.append(run_obj)
        
        # outside
        DRIVER.quit()
        print(lifts)
        print(runs)

        json_string = common.prepareForExport(lifts, runs, "copper")
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