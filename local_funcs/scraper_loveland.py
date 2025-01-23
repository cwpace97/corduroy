from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import local_common as common
import dbwriter

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

service = webdriver.ChromeService('/usr/bin/chromedriver')
DRIVER = webdriver.Chrome(options=chrome_options, service=service)
# DRIVER = webdriver.Chrome()

print("starting...")
web = "https://skiloveland.com/trail-lift-report"
DRIVER.get(web)

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

DRIVER.quit()
json_string = common.prepareForExport(lifts, runs, "loveland")
results = dbwriter.main(json_string)