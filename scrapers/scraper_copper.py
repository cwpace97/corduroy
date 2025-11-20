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
        time.sleep(5)
        
        # DEBUG: Save the page source for comparison
        try:
            with open('/data/selenium_copper.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("✅ Saved Selenium HTML to /data/selenium_copper.html")
        except Exception as e:
            print(f"⚠️ Could not save HTML: {e}")
        
        # Wait for accordion panels to be present
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[id*='accordion']"))
            )
            print("✓ Accordion panels detected")
        except Exception as e:
            print(f"⚠️ Warning: Timeout waiting for accordions: {e}")
        
        # Try to find and click the "All Lifts" accordion button
        try:
            all_lifts_button = self.driver.find_element(
                By.XPATH, 
                '//div[@id="sector-all-lifts-accordion"]//button[@class="panel-header btn"]'
            )
            print("Found 'All Lifts' button")
            
            # Check if the panel is already opened
            panel_body = self.driver.find_element(
                By.XPATH,
                '//div[@id="sector-all-lifts-accordion"]//div[@class="panel-body opened"]'
            )
            print("'All Lifts' panel is already open")
        except:
            # Panel is not open, try to click it
            try:
                all_lifts_button = self.driver.find_element(
                    By.XPATH, 
                    '//div[@id="sector-all-lifts-accordion"]//button'
                )
                print("Clicking 'All Lifts' button to expand")
                all_lifts_button.click()
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click 'All Lifts' button: {e}")
        
        lifts = []
        
        # Find the "All Lifts" accordion section by ID
        try:
            all_lifts_section = self.driver.find_element(By.ID, "sector-all-lifts-accordion")
            print("✓ Found 'All Lifts' section by ID")
            
            # Find tables within the All Lifts section
            tables = all_lifts_section.find_elements(By.TAG_NAME, "table")
            print(f"Found {len(tables)} tables in 'All Lifts' section")
            
            for table_idx, table in enumerate(tables):
                try:
                    # Check table headers
                    headers = table.find_elements(By.TAG_NAME, "th")
                    header_texts = [h.text.strip() for h in headers]
                    header_texts_lower = [h.lower() for h in header_texts]
                    
                    print(f"Table {table_idx+1} headers: {header_texts}")
                    
                    # Lift tables have 'Type' column, trail tables have 'Difficulty' column
                    has_type = 'type' in header_texts_lower
                    has_lift = 'lift' in header_texts_lower
                    has_difficulty = 'difficulty' in header_texts_lower
                    
                    # Skip trail tables (they have 'Difficulty' column)
                    if has_difficulty:
                        print(f"  Skipping table {table_idx+1} - trail table")
                        continue
                    
                    # Process lift table (has 'Type' and 'Lift' columns, no 'Difficulty')
                    if has_type and has_lift:
                        print(f"✓ Processing lift table {table_idx+1}")
                        
                        rows = table.find_elements(By.XPATH, ".//tbody/tr")
                        print(f"  Found {len(rows)} lift rows")
                        
                        for row in rows:
                            try:
                                # Get lift name
                                name_cell = row.find_element(By.CSS_SELECTOR, "td.name")
                                lift_name = name_cell.text.strip()
                                
                                if not lift_name:
                                    continue
                                
                                # Get lift type
                                type_cell = row.find_element(By.CSS_SELECTOR, "td.type")
                                lift_type = type_cell.text.strip()
                                
                                # Get lift status - check SVG fill color
                                status_cell = row.find_element(By.CSS_SELECTOR, "td.status")
                                is_open = False
                                
                                # Check all SVG path elements for fill color
                                try:
                                    # Get all path elements
                                    paths = status_cell.find_elements(By.TAG_NAME, "path")
                                    for path in paths:
                                        fill_attr = path.get_attribute("fill")
                                        if fill_attr:
                                            # Green (#8BC53F) = Open, Red (#D0021B) = Closed
                                            # Case-insensitive comparison
                                            fill_upper = fill_attr.upper()
                                            if "8BC53F" in fill_upper:
                                                is_open = True
                                                break
                                            elif "D0021B" in fill_upper:
                                                is_open = False
                                                break
                                except Exception as e:
                                    print(f"    Error checking lift status for {lift_name}: {e}")
                                
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
                    
        except Exception as e:
            print(f"❌ Error finding 'All Lifts' section: {e}")
        
        print(f"Total lifts parsed: {len(lifts)}")
        return lifts
    
    def parse_runs(self) -> list:
        """Parse runs data from Copper Mountain website"""
        print("Starting to parse runs...")
        
        runs = []
        
        # Find all accordion panels EXCEPT the "All Lifts" one
        try:
            # Get all accordion panels
            all_panels = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='ui-accordion-panel']")
            print(f"Found {len(all_panels)} accordion panels")
            
            for panel_idx, panel in enumerate(all_panels):
                try:
                    # Check if this is the "All Lifts" panel - skip it
                    panel_id = panel.get_attribute("id")
                    if panel_id == "sector-all-lifts-accordion":
                        print(f"  Skipping panel {panel_idx+1} - 'All Lifts' section")
                        continue
                    
                    # Check if panel is collapsed, if so expand it
                    panel_class = panel.get_attribute("class")
                    if "collapsed" in panel_class:
                        try:
                            # Find and click the button to expand this panel
                            expand_button = panel.find_element(By.CSS_SELECTOR, "button.panel-header")
                            print(f"  Expanding panel {panel_idx+1}")
                            expand_button.click()
                            time.sleep(1)  # Wait for panel to expand and content to load
                        except Exception as e:
                            print(f"  Could not expand panel {panel_idx+1}: {e}")
                    else:
                        print(f"  Panel {panel_idx+1} already open")
                    
                    # Find trail tables in this panel (tables with 'Difficulty' column)
                    tables = panel.find_elements(By.TAG_NAME, "table")
                    
                    for table_idx, table in enumerate(tables):
                        try:
                            # Check table headers
                            headers = table.find_elements(By.TAG_NAME, "th")
                            header_texts = [h.text.strip() for h in headers]
                            header_texts_lower = [h.lower() for h in header_texts]
                            
                            # Trail tables have 'Difficulty' column
                            has_difficulty = 'difficulty' in header_texts_lower
                            has_trail = 'trail' in header_texts_lower
                            has_type = 'type' in header_texts_lower
                            
                            # Skip lift tables (have 'Type' but no 'Difficulty')
                            if has_type and not has_difficulty:
                                continue
                            
                            # Process trail tables (have 'Difficulty' column)
                            if has_difficulty and has_trail:
                                print(f"✓ Processing trail table in panel {panel_idx+1}")
                                
                                # Get all data rows (skip header row)
                                rows = table.find_elements(By.XPATH, ".//tbody/tr")
                                print(f"  Found {len(rows)} trail rows")
                                
                                for row in rows:
                                    try:
                                        # Get trail name
                                        name_cell = row.find_element(By.CSS_SELECTOR, "td.name")
                                        run_name = name_cell.text.strip()
                                        
                                        if not run_name:
                                            continue
                                        
                                        # Get trail status - check SVG fill color
                                        status_cell = row.find_element(By.CSS_SELECTOR, "td.status")
                                        is_open = False
                                        
                                        # Look for the SVG path with fill color or "opening" class
                                        try:
                                            icon_div = status_cell.find_element(By.TAG_NAME, "div")
                                            class_attr = icon_div.get_attribute("class")
                                            if class_attr and "opening" in class_attr:
                                                is_open = True
                                        except:
                                            pass
                                        
                                        # Check SVG fill colors
                                        if not is_open:
                                            try:
                                                paths = status_cell.find_elements(By.XPATH, ".//path[@fill]")
                                                for path in paths:
                                                    fill_attr = path.get_attribute("fill")
                                                    if fill_attr:
                                                        # Green (#8BC53F) = Open, Red (#D0021B) = Closed
                                                        if "#8BC53F" in fill_attr.upper():
                                                            is_open = True
                                                            break
                                                        elif "#D0021B" in fill_attr.upper():
                                                            is_open = False
                                                            break
                                            except:
                                                pass
                                        
                                        # Get difficulty level
                                        difficulty_cell = row.find_element(By.CSS_SELECTOR, "td.difficulty")
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
                            print(f"Error processing table in panel {panel_idx+1}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing panel {panel_idx+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error finding accordion panels: {e}")
        
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