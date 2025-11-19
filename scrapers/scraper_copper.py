import common
import os
import time
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CopperScraper(BaseScraper):
    """Copper Mountain scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.coppercolorado.com/the-mountain/trail-lift-info/winter-trail-report")
        super().__init__("Copper", website_url)
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Copper Mountain website"""
        print("Starting to parse lifts...")
        
        # Wait for page to fully load
        time.sleep(3)
        
        # DEBUG: Save the page source for comparison
        try:
            with open('/data/selenium_copper.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("✅ Saved Selenium HTML to /data/selenium_copper.html")
        except Exception as e:
            print(f"⚠️ Could not save HTML: {e}")
        
        # Try to expand all collapsed panels to reveal all lift data
        try:
            # Look for panel buttons that might be collapsed
            panel_buttons = self.driver.find_elements(By.XPATH, '//button[contains(@class, "panel-toggle") or .//span[contains(@class, "panel")]]')
            print(f"Found {len(panel_buttons)} panel buttons")
            
            for i, button in enumerate(panel_buttons):
                try:
                    # Check if the panel is collapsed
                    parent = button.find_element(By.XPATH, './following-sibling::div[contains(@class, "panel-body")]')
                    if 'collapsed' in parent.get_attribute('class'):
                        print(f"Expanding panel {i+1}")
                        button.click()
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Could not check/click panel {i+1}: {e}")
        except Exception as e:
            print(f"Error expanding panels: {e}")
        
        # Wait after expanding panels
        time.sleep(2)
        
        lifts = []
        
        # Wait for tables to be present and rendered
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✓ Tables detected on page")
        except Exception as e:
            print(f"⚠️ Warning: Timeout waiting for tables: {e}")
        
        # Find all tables on the page
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            try:
                # Check if this is a lift table by looking at headers
                headers = table.find_elements(By.TAG_NAME, "th")
                header_texts = [h.text.strip() for h in headers]
                header_texts_lower = [h.lower() for h in header_texts]
                
                # DEBUG: Print headers for each table
                if header_texts:
                    print(f"Table {table_idx+1} headers: {header_texts}")
                
                # Lift tables have 'Type' column, trail tables have 'Difficulty' column
                # Use case-insensitive matching
                has_type = 'type' in header_texts_lower
                has_lift = 'lift' in header_texts_lower
                
                if has_type and has_lift:
                    print(f"✓ Processing lift table {table_idx+1}")
                    
                    # Get all data rows (skip header row)
                    rows = table.find_elements(By.XPATH, ".//tbody/tr")
                    
                    for row in rows:
                        try:
                            # Get lift name
                            name_cell = row.find_element(By.CLASS_NAME, "name")
                            lift_name = name_cell.text.strip()
                            
                            if not lift_name:
                                continue
                            
                            # Get lift type
                            type_cell = row.find_element(By.CLASS_NAME, "type")
                            lift_type = type_cell.text.strip()
                            
                            # Get lift status (check for green checkmark)
                            status_cell = row.find_element(By.CLASS_NAME, "status")
                            
                            # Check status using multiple methods for robustness
                            is_open = False
                            
                            # Method 1: Check for green/red fill in path elements
                            all_paths = status_cell.find_elements(By.TAG_NAME, "path")
                            for path in all_paths:
                                fill_attr = path.get_attribute("fill")
                                if fill_attr:
                                    if "#8BC53F" in fill_attr.upper():  # Green = Open
                                        is_open = True
                                        break
                                    elif "#D0021B" in fill_attr.upper():  # Red = Closed
                                        is_open = False
                                        break
                            
                            # Method 2: Check for class indicators as backup
                            if not is_open:
                                try:
                                    icon_div = status_cell.find_element(By.TAG_NAME, "div")
                                    class_attr = icon_div.get_attribute("class")
                                    if class_attr and "opening" in class_attr:
                                        is_open = True
                                except:
                                    pass
                            
                            lift_obj = {
                                "liftName": lift_name,
                                "liftType": lift_type,
                                "liftStatus": is_open,
                            }
                            lifts.append(lift_obj)
                            print(f"  Added lift: {lift_name} ({lift_type}) - Open: {is_open}")
                            
                        except Exception as e:
                            print(f"  Error parsing lift row: {e}")
                            continue
                            
            except Exception as e:
                print(f"Error processing table {table_idx+1}: {e}")
                continue
        
        print(f"Total lifts parsed: {len(lifts)}")
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Copper Mountain website"""
        print("Starting to parse runs...")
        
        runs = []
        
        # Find all tables on the page
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            try:
                # Check if this is a trail table by looking at headers
                headers = table.find_elements(By.TAG_NAME, "th")
                header_texts = [h.text.strip() for h in headers]
                header_texts_lower = [h.lower() for h in header_texts]
                
                # DEBUG: Print headers for each table (if not already printed in lifts)
                if header_texts:
                    print(f"Table {table_idx+1} headers: {header_texts}")
                
                # Trail tables have 'Difficulty' column, lift tables have 'Type' column
                # Use case-insensitive matching
                has_difficulty = 'difficulty' in header_texts_lower
                has_trail = 'trail' in header_texts_lower
                
                if has_difficulty and has_trail:
                    print(f"✓ Processing trail table {table_idx+1}")
                    
                    # Get all data rows (skip header row)
                    rows = table.find_elements(By.XPATH, ".//tbody/tr")
                    
                    for row in rows:
                        try:
                            # Get trail name
                            name_cell = row.find_element(By.CLASS_NAME, "name")
                            run_name = name_cell.text.strip()
                            
                            if not run_name:
                                continue
                            
                            # Get trail status (check for green checkmark)
                            status_cell = row.find_element(By.CLASS_NAME, "status")
                            
                            # Check status using multiple methods for robustness
                            is_open = False
                            
                            # Method 1: Check for green/red fill in path elements
                            all_paths = status_cell.find_elements(By.TAG_NAME, "path")
                            for path in all_paths:
                                fill_attr = path.get_attribute("fill")
                                if fill_attr:
                                    if "#8BC53F" in fill_attr.upper():  # Green = Open
                                        is_open = True
                                        break
                                    elif "#D0021B" in fill_attr.upper():  # Red = Closed
                                        is_open = False
                                        break
                            
                            # Method 2: Check for class indicators as backup
                            if not is_open:
                                try:
                                    icon_div = status_cell.find_element(By.TAG_NAME, "div")
                                    class_attr = icon_div.get_attribute("class")
                                    if class_attr and "opening" in class_attr:
                                        is_open = True
                                except:
                                    pass
                            
                            # Get difficulty level
                            difficulty_cell = row.find_element(By.CLASS_NAME, "difficulty")
                            difficulty_div = difficulty_cell.find_element(By.TAG_NAME, "div")
                            difficulty_class = difficulty_div.get_attribute("class")
                            
                            # Map difficulty classes to standard levels
                            if "difficulty-level-green" in difficulty_class:
                                run_difficulty = "green"
                            elif "difficulty-level-blue" in difficulty_class:
                                run_difficulty = "blue1"
                            elif "difficulty-level-black-3" in difficulty_class:
                                run_difficulty = "black3"
                            elif "difficulty-level-black-2" in difficulty_class:
                                run_difficulty = "black2"
                            elif "difficulty-level-black" in difficulty_class:
                                run_difficulty = "black1"
                            else:
                                print(f"  Unknown difficulty for {run_name}: {difficulty_class}")
                                continue
                            
                            run_obj = {
                                "runName": run_name,
                                "runStatus": is_open,
                                "runDifficulty": run_difficulty,
                            }
                            runs.append(run_obj)
                            print(f"  Added trail: {run_name} ({run_difficulty}) - Open: {is_open}")
                            
                        except Exception as e:
                            print(f"  Error parsing trail row: {e}")
                            continue
                            
            except Exception as e:
                print(f"Error processing table {table_idx+1}: {e}")
                continue
        
        print(f"Total trails parsed: {len(runs)}")
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