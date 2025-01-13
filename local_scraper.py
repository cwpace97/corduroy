from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
import pandas as pd
from datetime import datetime as dt
import json

# X PATH SYNTAX
# //tagName[@AttributeName="Value"]
# //span[@class="panel-icon"]

CHECKMARK_COLOR = "#8BC53F"
X_COLOR = "#D0021B"

DRIVER = webdriver.Chrome()

def lambda_handler(event, context):
    print("starting...")
    copper = "https://www.coppercolorado.com/the-mountain/trail-lift-info/winter-trail-report"
    DRIVER.get(copper)

    # open lift menus
    for button in DRIVER.find_elements(By.XPATH, '//span[@class="panel-icon"]'):
        button.click()

    # each row within all the tables
    runs = []
    lifts = []
    rows = DRIVER.find_elements(By.TAG_NAME, "tr")
    for run in rows:
        print(run.text)
        if isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
            #TODO
            lift_name, lift_status, lift_type = None, None, None
            lift_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
            lift_status = isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']")
            lift_type = run.find_element(By.CLASS_NAME, "type").get_attribute("innerHTML")
            
            lift_obj = {
                "Lift_Name": lift_name,
                "Lift_Type": lift_type,
                "Lift_Status": lift_status,
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
                "Run_Name": run_name,
                "Run_Status": run_status,
                "Run_Difficulty": run_difficulty,
            }
            runs.append(run_obj)
    
    # outside
    print(lifts)
    print(runs)

    # prep for export/update
    lifts_set = {each['Lift_Name'] : each for each in lifts}.values()
    runs_set = {each['Run_Name'] : each for each in runs}.values()
    now = dt.today()
    formatted = now.strftime("%Y-%m-%d")
    message = {
        "updatedDate": formatted,
        "location": "copper",
        "lifts": lifts_set,
        "runs": runs_set
    }
    print(message)
    json_string = json.dumps(message)

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