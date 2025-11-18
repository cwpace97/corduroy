import common
import os
import time
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WinterParkScraper(BaseScraper):
    """Winter Park Resort scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.winterparkresort.com/the-mountain/mountain-report#lift-and-trail-status")
        super().__init__("WinterPark", website_url)
    
    def wait_for_react_app(self):
        """Wait for the React app to load and render content"""
        print("Waiting for React app to load...")
        try:
            # Wait for the root div to have content (React has rendered)
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.find_element(By.ID, "root").get_attribute("innerHTML").strip() != ""
            )
            print("✓ React app loaded")
            
            # Additional wait for lift/trail data to render
            time.sleep(5)
            
            # Try to wait for lift or trail elements
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(driver.find_elements(By.XPATH, '//li[contains(@class, "Lift") or contains(@class, "Trail")]')) > 0
                )
                print("✓ Lift/trail data rendered")
            except:
                print("⚠️ Timeout waiting for lift/trail elements")
                
        except Exception as e:
            print(f"⚠️ Error waiting for React app: {e}")
        
        # Save page source for debugging
        try:
            with open('/data/winterpark_debug.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("✓ Saved page source to /data/winterpark_debug.html")
        except:
            pass
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Winter Park website"""
        print("Starting to parse lifts...")
        
        # Wait for React app to load
        self.wait_for_react_app()
        
        # Try multiple selectors
        selectors = [
            '//li[contains(@class, "Lift")]',
            '//div[contains(@class, "Lift")]',
            '//*[contains(@class, "lift-")]',
            '//*[contains(text(), "lift") or contains(text(), "Lift")]/..',
        ]
        
        rows = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    rows = elements
                    break
            except:
                continue
        
        if not rows:
            print("❌ No lift elements found with any selector")
            return []
        
        lifts = []
        for row in rows:
            try:
                # Try to find lift name
                lift_name = None
                name_selectors = [
                    './/p[contains(@class, "name")]',
                    './/span[contains(@class, "name")]',
                    './/div[contains(@class, "name")]',
                    './/*[contains(@class, "name")]',
                ]
                
                for ns in name_selectors:
                    try:
                        elem = row.find_element(By.XPATH, ns)
                        lift_name = elem.text or elem.get_attribute("innerHTML")
                        if lift_name and lift_name.strip():
                            lift_name = lift_name.strip()
                            break
                    except:
                        continue
                
                if not lift_name or len(lift_name) < 2:
                    continue
                
                # Determine lift STATUS
                lift_status = False
                status_indicators = [
                    './/*[name()="svg"][contains(@data-src, "open")]',
                    './/*[contains(@class, "open")]',
                    './/*[contains(text(), "Open") or contains(text(), "open")]',
                ]
                
                for si in status_indicators:
                    if common.isElementPresent(row, By.XPATH, si):
                        lift_status = True
                        break
                
                # Determine CHAIR TYPE
                lift_type = "Unknown"
                type_checks = [
                    ('.//*[name()="svg"][contains(@data-src, "cabriolet")]', "Cabriolet"),
                    ('.//*[name()="svg"][contains(@data-src, "magic_carpet")]', "Magic Carpet"),
                    ('.//*[name()="svg"][contains(@data-src, "double")]', "Double"),
                    ('.//*[name()="svg"][contains(@data-src, "triple")]', "Triple"),
                    ('.//*[name()="svg"][contains(@data-src, "quad")]', "Quad"),
                    ('.//*[name()="svg"][contains(@data-src, "six")]', "Six"),
                    ('.//*[name()="svg"][contains(@data-src, "rope_tow")]', "Tow Rope"),
                ]
                
                for check_xpath, type_name in type_checks:
                    if common.isElementPresent(row, By.XPATH, check_xpath):
                        lift_type = type_name
                        break
                
                lift_obj = {
                    "liftName": lift_name,
                    "liftType": lift_type,
                    "liftStatus": lift_status,
                }
                lifts.append(lift_obj)
                print(f"  ✓ Added lift: {lift_name} ({lift_type}) - Open: {lift_status}")
                
            except Exception as e:
                print(f"  ⚠️ Error parsing lift: {e}")
                continue

        print(f"Total lifts parsed: {len(lifts)}")
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Winter Park website"""
        print("Starting to parse runs...")
        
        # Try multiple selectors for trails
        selectors = [
            '//li[contains(@class, "TrailWidget")]',
            '//li[contains(@class, "Trail")]',
            '//div[contains(@class, "Trail")]',
            '//*[contains(@class, "trail-")]',
        ]
        
        rows = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"Found {len(elements)} trail elements with selector: {selector}")
                    rows = elements
                    break
            except:
                continue
        
        if not rows:
            print("❌ No trail elements found with any selector")
            return []
        
        runs = []
        for row in rows:
            try:
                # Try to find run name
                run_name = None
                name_selectors = [
                    './/p[contains(@class, "name")]',
                    './/span[contains(@class, "name")]',
                    './/div[contains(@class, "name")]',
                    './/*[contains(@class, "name")]',
                ]
                
                for ns in name_selectors:
                    try:
                        elem = row.find_element(By.XPATH, ns)
                        run_name = elem.text or elem.get_attribute("innerHTML")
                        if run_name and run_name.strip():
                            run_name = run_name.strip()
                            break
                    except:
                        continue
                
                if not run_name or len(run_name) < 2:
                    continue
                
                # Try to find status
                run_status = False
                try:
                    status_elem = row.find_element(By.XPATH, './/*[contains(@class, "status")]')
                    status_text = status_elem.text or status_elem.get_attribute("innerHTML")
                    run_status = "open" in status_text.lower() if status_text else False
                except:
                    pass
                
                # Determine GROOMING status
                run_groomed = False
                if common.isElementPresent(row, By.XPATH, './/*[name()="svg"][contains(@data-src, "grooming") or contains(@data-src, "groomed")]'):
                    run_groomed = True

                # Determine DIFFICULTY based on SVG icons
                run_difficulty = "Unknown"
                difficulty_checks = [
                    ('.//*[name()="svg"][contains(@data-src, "green-circle")]', "green"),
                    ('.//*[name()="svg"][contains(@data-src, "blue-square")]', "blue1"),
                    ('.//*[name()="svg"][contains(@data-src, "blue-black-square")]', "blue2"),
                    ('.//*[contains(@class, "green") or contains(@data-src, "green")]', "green"),
                    ('.//*[contains(@class, "blue") or contains(@data-src, "blue")]', "blue1"),
                    ('.//*[name()="svg"][contains(@data-src, "double-black-diamond") or contains(@data-src, "double_black")]', "black2"),
                    ('.//*[name()="svg"][contains(@data-src, "black-diamond") or contains(@data-src, "black_diamond")]', "black1"),
                    ('.//*[name()="svg"][contains(@data-src, "park") or contains(@data-src, "terrain")]', "terrainpark"),
                    ('.//*[contains(@class, "black")]', "black1"),
                ]
                
                for check_xpath, diff_level in difficulty_checks:
                    if common.isElementPresent(row, By.XPATH, check_xpath):
                        run_difficulty = diff_level
                        break
                
                if run_difficulty == "Unknown":
                    print(f"  ⚠️ Skipping run - unknown difficulty: {run_name}")
                    continue
                
                run_obj = {
                    "runName": run_name,
                    "runStatus": run_status,
                    "runDifficulty": run_difficulty,
                    "runGroomed": run_groomed
                }
                runs.append(run_obj)
                print(f"  ✓ Added trail: {run_name} ({run_difficulty}) - Open: {run_status}")
                
            except Exception as e:
                print(f"  ⚠️ Error parsing trail: {e}")
                continue

        print(f"Total trails parsed: {len(runs)}")
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
