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
        print("Starting to parse lifts...")
        lifts = []
        
        # Find h2 elements with the tablepress-table-name class (these are lift headers)
        lift_headers = self.driver.find_elements(By.CSS_SELECTOR, "h2.tablepress-table-name")
        print(f"Found {len(lift_headers)} lift headers")
        
        for header in lift_headers:
            try:
                # Get the full text (e.g., "Rainbow Magic Carpet - CLOSED" or "Chet's Dream -OPEN")
                full_text = header.text.strip()
                
                if not full_text:
                    continue
                
                # Try to split by " - " first (space-hyphen-space)
                if ' - ' in full_text:
                    parts = full_text.rsplit(' - ', 1)
                # If not found, try " -" (space-hyphen with no trailing space)
                elif ' -' in full_text:
                    parts = full_text.rsplit(' -', 1)
                # If not found, try "- " (hyphen-space with no leading space)
                elif '- ' in full_text:
                    parts = full_text.rsplit('- ', 1)
                else:
                    # No separator found, skip
                    print(f"  Skipping header (no separator): {full_text}")
                    continue
                
                if len(parts) != 2:
                    print(f"  Skipping header (couldn't split): {full_text}")
                    continue
                
                lift_name = parts[0].strip()
                status_text = parts[1].strip().upper()
                
                # Determine status (OPEN or CLOSED)
                lift_status = "OPEN" in status_text
                
                # Extract lift type from the name or set default
                lift_type = "Unknown"
                name_lower = lift_name.lower()
                if "carpet" in name_lower or "magic carpet" in name_lower:
                    lift_type = "Carpet"
                elif "chair" in name_lower or "quad" in name_lower or "triple" in name_lower or "double" in name_lower:
                    if "quad" in name_lower:
                        lift_type = "Quad"
                    elif "triple" in name_lower:
                        lift_type = "Triple"
                    elif "double" in name_lower:
                        lift_type = "Double"
                    else:
                        lift_type = "Chair"
                elif "poma" in name_lower or "platter" in name_lower:
                    lift_type = "Surface"
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)
                print(f"  Added lift: {lift_name} ({lift_type}) - Open: {lift_status}")
                
            except Exception as e:
                print(f"  Error parsing lift: {e}")
                continue
        
        print(f"Total lifts parsed: {len(lifts)}")
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