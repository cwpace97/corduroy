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

        # RUNS
        runs = []
        rows = DRIVER.find_elements(By.TAG_NAME, "tr")
        for run in rows:
            try:
                # DIFFICULTY
                if common.isElementPresent(run, By.XPATH, './/img[contains(@src, "beginner")]'):
                    run_difficulty = "green"
                elif common.isElementPresent(run, By.XPATH, './/img[contains(@src, "more_difficult")]'):
                    run_difficulty = "blue1"
                elif common.isElementPresent(run, By.XPATH, './/img[contains(@src, "most_difficult")]'):
                    run_difficulty = "black1"
                elif common.isElementPresent(run, By.XPATH, './/img[contains(@src, "expert")]'):
                    run_difficulty = "black2"
                elif common.isElementPresent(run, By.XPATH, './/img[contains(@src, "terrainpark")]'):
                    run_difficulty = "terrainpark"
                else:
                    continue

                # OPEN/CLOSE
                run_status = False
                if common.isElementPresent(run, By.XPATH, './/img[contains(@src, "open")]'):
                    run_status=True

                # GROOMING
                run_groomed = False
                if common.isElementPresent(run, By.XPATH, './/img[contains(@src, "grooming")]'):
                    run_groomed=True

                # NAME
                run_name = run.find_element(By.CLASS_NAME, "column-3").get_attribute("innerHTML")

                # AREA OF LOVELAND
                run_area = run.find_element(By.CLASS_NAME, "column-5").get_attribute("innerHTML")

                # print(f"{run_name}, {run_area}, {run_difficulty}, {run_groomed}, {run_status}")
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                    "runArea": run_area,
                    "runGroomed": run_groomed
                }
                runs.append(run_obj)
            except Exception as e:
                print("skipping run")

        # LIFTS
        lifts = []
        rows = DRIVER.find_elements(By.TAG_NAME, "h2")
        for row in rows:
            try:
                lift_name, lift_status_txt = row.get_attribute('innerHTML').split(' - ')
                lift_status = False
                if "OPEN" in lift_status_txt:
                    lift_status = True
                lift_obj = {
                    "liftName": lift_name,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)
            except Exception as e:
                print("skipping lift")

        # outside
        DRIVER.quit()
        print(lifts)
        print(runs)

        json_string = common.prepareForExport(lifts, runs, "loveland")
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

if __name__ == "__main__":
    handler("event","context")