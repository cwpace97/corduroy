import json
from datetime import datetime as dt
from pytz import timezone

from selenium.common.exceptions import *

def prepareForExport(lifts, runs, location):
    # prep for export/update
    lifts_set = {each['liftName'] : each for each in lifts}.values()
    runs_set = {each['runName'] : each for each in runs}.values()
    now = dt.now(tz=timezone("America/Denver"))
    formatted = now.strftime("%Y-%m-%d")
    message = {
        "updatedDate": formatted,
        "location": location,
        "lifts": list(lifts_set),
        "runs": list(runs_set)
    }
    print(message)
    return json.dumps(message)


def isElementPresent(driver, lookupType, locatorKey):
    try:
        # print("a")
        driver.find_element(lookupType, locatorKey)
        return True
    except NoSuchElementException as nse:
        # print("b")
        return False
    except StaleElementReferenceException as sere:
        # print("c")
        # return isElementPresent(DRIVER, lookupType, locatorKey)
        return False

def safeSearch(driver, lookupType, locatorKey):
    if isElementPresent(driver, lookupType, locatorKey):
        return driver.find_element(lookupType, locatorKey)
    return False