import common
import os
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By


class WinterParkScraper(BaseScraper):
    """Winter Park Resort scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.winterparkresort.com/the-mountain/mountain-report#lift-and-trail-status")
        super().__init__("WinterPark", website_url)
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Winter Park website"""
        rows = self.driver.find_elements(By.XPATH, '//li[contains(@class, "Lift")]')
        lifts = []
        for row in rows:
            try:
                lift_name = common.safeSearch(row, By.XPATH, './/p[contains(@class, "Lift_name")]').get_attribute("innerHTML")
                
                # Determine lift STATUS
                lift_status = False
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "open")]'):
                    lift_status = True
                
                # Determine CHAIR TYPE
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
                lifts.append(lift_obj)
            except Exception as e:
                print("skipping lift row")

        print(f"Found {len(lifts)} lifts")
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Winter Park website"""
        rows = self.driver.find_elements(By.XPATH, '//li[contains(@class, "TrailWidget")]')
        runs = []
        for row in rows:
            try:
                run_name = common.safeSearch(row, By.XPATH, './/p[contains(@class, "name")]').get_attribute("innerHTML")
                run_status_raw = common.safeSearch(row, By.XPATH, './/p[contains(@class, "status")]').get_attribute("innerHTML")
                
                # Convert status text to boolean
                run_status = "open" in run_status_raw.lower() if run_status_raw else False
                
                # Determine GROOMING status
                run_groomed = False
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "grooming")]'):
                    run_groomed = True

                # Determine DIFFICULTY based on SVG icons
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
                    print("Skipping run - unknown difficulty")
                    continue
                
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                    "runGroomed": run_groomed
                }
                runs.append(run_obj)
            except Exception as e:
                print("skipping run row")

        return runs


# Create scraper instance
winterpark_scraper = WinterParkScraper()

def scrape_winterpark():
    """Main scraping function for Winter Park Resort"""
    return winterpark_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_winterpark()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_winterpark()
    print(f"Final result: {result}")