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

        # LIFTS
        rows = DRIVER.find_elements(By.XPATH, '//li[contains(@class, "Lift")]')
        lifts = []
        for row in rows:
            try:
                lift_name = common.safeSearch(row, By.XPATH, './/p[contains(@class, "Lift_name")]').get_attribute("innerHTML")
                
                # STATUS
                lift_status = False
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "open")]'):
                    lift_status = True
                
                # CHAIRTYPE
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "cabriolet")]'):
                    lift_type = "Cabriolet"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "magic_carpet")]'):
                    lift_type = "Magic Carpet"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "double")]'):
                    lift_type = "Double"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "triple")]'):
                    lift_type = "Triple"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "quad")]'):
                    lift_type = "Quad"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "six")]'):
                    lift_type = "Six"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "rope_tow")]'):
                    lift_type = "Tow Rope"
                else:
                    continue
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                # print(lift_obj)
                lifts.append(lift_obj)
            except Exception as e:
                print("skipping row")

        print(lifts)

        # RUNS
        rows = DRIVER.find_elements(By.XPATH, '//li[contains(@class, "TrailWidget")]')
        runs = []
        for row in rows:
            try:
                run_name = common.safeSearch(row, By.XPATH, './/p[contains(@class, "name")]').get_attribute("innerHTML")
                run_status = common.safeSearch(row, By.XPATH, './/p[contains(@class, "status")]').get_attribute("innerHTML")
                
                # GROOMED
                run_groomed = False
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "grooming")]'):
                    run_groomed = True

                # DIFFICULTY
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "green-circle")]'):
                    run_difficulty = "green"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "blue-square")]'):
                    run_difficulty = "blue"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "blue-black-square")]'):
                    run_difficulty = "blue2"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "black-diamond")]'):
                    run_difficulty = "black1"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "double-black-diamond")]'):
                    run_difficulty = "black2"
                elif common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "park")]'):
                    run_difficulty = "terrainpark"
                else:
                    print("AA")
                    continue
                
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                    "runGroomed": run_groomed
                }
                runs.append(run_obj)
            except Exception as e:
                print("skipping row")

        # outside
        DRIVER.quit()
        print(lifts)
        print(runs)

        json_string = common.prepareForExport(lifts, runs, "winterpark")
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