from selenium import webdriver
from selenium.webdriver.common.by import By

import local_common as common
import dbwriter

DRIVER = webdriver.Chrome()
print("starting...")
web = "https://www.winterparkresort.com/the-mountain/mountain-report#lift-and-trail-status"
DRIVER.get(web)

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

# print(lifts)
# RUNS
rows = DRIVER.find_elements(By.XPATH, '//li[contains(@class, "TrailWidget")]')
runs = []
for row in rows:
    try:
        run_name = common.safeSearch(row, By.XPATH, './/p[contains(@class, "name")]').get_attribute("innerHTML")
        
        run_status = False
        if "open" in common.safeSearch(row, By.XPATH, './/p[contains(@class, "status")]').get_attribute("innerHTML").lower():
            run_status = True
        
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
        # print(run_obj)
        runs.append(run_obj)
    except Exception as e:
        print("skipping row")

json_string = common.prepareForExport(lifts, runs, "winterpark")
results = dbwriter.main(json_string)