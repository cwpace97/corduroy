import common
import os
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By


class CopperScraper(BaseScraper):
    """Copper Mountain scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.coppercolorado.com/the-mountain/trail-lift-info/winter-trail-report")
        super().__init__("Copper", website_url)
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Copper Mountain website"""
        # Open lift menus first
        for button in self.driver.find_elements(By.XPATH, '//span[@class="panel-icon"]'):
            button.click()
        print("Menus opened")
        
        lifts = []
        rows = self.driver.find_elements(By.TAG_NAME, "tr")
        
        for run in rows:
            if common.isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
                # This is a lift row
                lift_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                lift_status = common.isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']")
                lift_type = run.find_element(By.CLASS_NAME, "type").get_attribute("innerHTML")
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)
        
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Copper Mountain website"""
        runs = []
        rows = self.driver.find_elements(By.TAG_NAME, "tr")
        
        for run in rows:
            if not common.isElementPresent(run, By.XPATH, ".//*[name()='td'][@class='type']"):
                # This is a run row (not a lift row)
                try:
                    run_name = run.find_element(By.CLASS_NAME, "name").get_attribute("innerHTML")
                    run_status = common.isElementPresent(run, By.XPATH, ".//*[name()='path'][@fill='#8BC53F']")
                    
                    # Determine difficulty
                    difficulty_text = run.find_element(By.CLASS_NAME, "difficulty").find_element(By.TAG_NAME, "div").get_attribute("class")
                    if "icon difficulty-level-green" in difficulty_text: 
                        run_difficulty = "green"
                    elif "icon difficulty-level-blue" in difficulty_text: 
                        run_difficulty = "blue1"
                    elif "icon difficulty-level-black-3" in difficulty_text: 
                        run_difficulty = "black3"
                    elif "icon difficulty-level-black-2" in difficulty_text: 
                        run_difficulty = "black2"
                    elif "icon difficulty-level-black" in difficulty_text: 
                        run_difficulty = "black1"
                    else:
                        print("Skipping run - difficulty not found")
                        continue
                    
                    run_obj = {
                        "runName": run_name,
                        "runStatus": run_status,
                        "runDifficulty": run_difficulty,
                    }
                    runs.append(run_obj)
                except Exception as e:
                    print("Skipping run - difficulty not found")
                    continue
        
        return runs


# Create scraper instance
copper_scraper = CopperScraper()

def scrape_copper():
    """Main scraping function for Copper Mountain"""
    return copper_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_copper()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_copper()
    print(f"Final result: {result}")