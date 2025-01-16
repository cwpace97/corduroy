import json
from datetime import datetime as dt
from pytz import timezone
from tempfile import mkdtemp

from selenium.common.exceptions import *

def setChromeConfigOptions(chrome_options):
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
    return chrome_options

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


def isElementPresent(DRIVER, lookupType, locatorKey):
    try:
        # print("a")
        DRIVER.find_element(lookupType, locatorKey)
        return True
    except NoSuchElementException as nse:
        # print("b")
        return False
    except StaleElementReferenceException as sere:
        # print("c")
        # return isElementPresent(DRIVER, lookupType, locatorKey)
        return False

def safeSearch(DRIVER, lookupType, locatorKey):
    try:
        element = DRIVER.find_element(lookupType, locatorKey)
        return element
    except NoSuchElementException as e:
        return None