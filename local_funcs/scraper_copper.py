from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import local_common as common
import dbwriter

DRIVER = webdriver.Chrome()
print("starting...")
web = "https://www.coppercolorado.com/the-mountain/trail-lift-info/winter-trail-report"
DRIVER.get(web)

# open lift menus
for button in DRIVER.find_elements(By.XPATH, '//span[@class="panel-icon"]'):
    button.click()

# each row within all the tables
runs = []
lifts = []
rows = DRIVER.find_elements(By.TAG_NAME, "tr")
for run in rows:
    if common.isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
        # LIFTS
        lift_name, lift_status, lift_type = None, None, None
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
        # RUNS
        run_name, run_status, run_difficulty = None, None, None

        run_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
        run_status = common.isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']") 
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

DRIVER.quit()
json_string = common.prepareForExport(lifts, runs, "copper")
results = dbwriter.main(json_string)