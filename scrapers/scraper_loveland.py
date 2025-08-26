import common
import os
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By


class LovelandScraper(BaseScraper):
    """Loveland Ski Area scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://skiloveland.com/trail-lift-report/")
        super().__init__("Loveland", website_url)
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Loveland website"""
        lifts = []
        rows = self.driver.find_elements(By.TAG_NAME, "h2")
        print(f"Found {len(rows)} lift headers to process")
        
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
                print(f"Skipping lift due to error: {e}")
        
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Loveland website"""
        runs = []
        rows = self.driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} table rows to process")
        
        for run in rows:
            try:
                # Determine DIFFICULTY based on images
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

                # Determine OPEN/CLOSE status
                run_status = False
                if common.isElementPresent(run, By.XPATH, './/img[contains(@src, "open")]'):
                    run_status = True

                # Determine GROOMING status
                run_groomed = False
                if common.isElementPresent(run, By.XPATH, './/img[contains(@src, "grooming")]'):
                    run_groomed = True

                # Extract run NAME
                run_name = run.find_element(By.CLASS_NAME, "column-3").get_attribute("innerHTML")

                # Extract AREA of Loveland
                run_area = run.find_element(By.CLASS_NAME, "column-5").get_attribute("innerHTML")

                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                    "runArea": run_area,
                    "runGroomed": run_groomed
                }
                runs.append(run_obj)
            except Exception as e:
                print(f"Skipping run due to error: {e}")
        
        return runs


# Create scraper instance
loveland_scraper = LovelandScraper()

def scrape_loveland():
    """Main scraping function for Loveland Ski Area"""
    return loveland_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_loveland()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_loveland()
    print(f"Final result: {result}")