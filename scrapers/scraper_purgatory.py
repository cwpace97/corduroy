import common
import os
import time
import re
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class PurgatoryScraper(BaseScraper):
    """Purgatory Resort scraper - parses lift and trail data from HTML"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.purgatory.ski/mountain/weather-conditions-webcams/")
        super().__init__("Purgatory", website_url)
    
    def get_page_soup(self):
        """Get BeautifulSoup object from page source"""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            return soup
            
        except Exception as e:
            print(f"❌ Error getting page soup: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Purgatory website HTML"""
        print("Starting to parse lifts...")
        
        try:
            soup = self.get_page_soup()
            if not soup:
                return []
            
            lifts = []
            
            # Find the lifts list - it's in the tab panel with id="m-tab-lifts"
            lifts_panel = soup.find('div', {'id': 'm-tab-lifts'})
            if not lifts_panel:
                print("❌ Could not find lifts panel")
                return []
            
            # Find all lift items
            lift_items = lifts_panel.find_all('li', class_=re.compile(r'm-lift-status-'))
            print(f"Found {len(lift_items)} lift items")
            
            for lift_item in lift_items:
                try:
                    # Get lift name from h3 element
                    name_elem = lift_item.find('h3', class_='m-lift-header')
                    if not name_elem:
                        continue
                    lift_name = name_elem.get_text(strip=True)
                    
                    # Determine status from class
                    classes = lift_item.get('class', [])
                    is_open = 'm-lift-status-open' in classes
                    
                    # Get lift type from icon image
                    lift_type = self.extract_lift_type(lift_item)
                    
                    lift_obj = {
                        "liftName": lift_name,
                        "liftType": lift_type,
                        "liftStatus": is_open
                    }
                    
                    lifts.append(lift_obj)
                    print(f"  ✓ Added lift: {lift_name} ({lift_type}) - Open: {is_open}")
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing lift: {e}")
                    continue
            
            print(f"Total lifts parsed: {len(lifts)}")
            return lifts
            
        except Exception as e:
            print(f"❌ Error parsing lifts: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_lift_type(self, lift_item) -> str:
        """Extract lift type from the icon image source"""
        img = lift_item.find('img')
        if not img:
            return 'Chair'
        
        src = img.get('src', '')
        
        # Map icon filenames to lift types
        if '6-person' in src:
            return 'Six-Person Chair'
        elif '4-person' in src:
            return 'Quad Chair'
        elif '3-person' in src:
            return 'Triple Chair'
        elif '2-person' in src:
            return 'Double Chair'
        elif 'magic-carpet' in src:
            return 'Magic Carpet'
        elif 'gondola' in src:
            return 'Gondola'
        else:
            return 'Chair'
    
    def map_difficulty(self, trail_classes: list) -> str:
        """Map trail difficulty from CSS classes"""
        if 'm-filter-value-double-black' in trail_classes:
            return 'black2'
        elif 'm-filter-value-black' in trail_classes:
            return 'black1'
        elif 'm-filter-value-blue' in trail_classes or 'm-filter-value-double-blue' in trail_classes:
            return 'blue1'
        elif 'm-filter-value-green' in trail_classes:
            return 'green'
        else:
            return 'blue1'
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Purgatory website HTML"""
        print("Starting to parse runs...")
        
        try:
            soup = self.get_page_soup()
            if not soup:
                return []
            
            runs = []
            
            # Find the trails panel
            trails_panel = soup.find('div', {'id': 'm-tab-trails'})
            if not trails_panel:
                print("❌ Could not find trails panel")
                return []
            
            # Find all area accordions
            area_accordions = trails_panel.find_all('li', class_='m-accordion')
            print(f"Found {len(area_accordions)} trail areas")
            
            for area in area_accordions:
                try:
                    # Get area name
                    area_header = area.find('h3', class_='m-lift-header')
                    area_name = area_header.get_text(strip=True) if area_header else 'Unknown'
                    
                    # Find all trails in this area
                    trail_items = area.find_all('li', class_='m-filter-target')
                    print(f"Processing area: {area_name} ({len(trail_items)} trails)")
                    
                    for trail_item in trail_items:
                        try:
                            # Get trail name from h4 element
                            name_elem = trail_item.find('h4')
                            if not name_elem:
                                continue
                            run_name = name_elem.get_text(strip=True)
                            
                            # Get classes for status and difficulty
                            classes = trail_item.get('class', [])
                            
                            # Determine open/closed status
                            is_open = 'm-filter-value-open' in classes
                            
                            # Determine groomed status
                            is_groomed = 'm-filter-value-groomed' in classes
                            
                            # Determine difficulty
                            run_difficulty = self.map_difficulty(classes)
                            
                            run_obj = {
                                "runName": run_name,
                                "runStatus": is_open,
                                "runDifficulty": run_difficulty,
                                "runArea": area_name,
                                "runGroomed": is_groomed
                            }
                            
                            runs.append(run_obj)
                            status_str = "Open" if is_open else "Closed"
                            groomed_str = ", Groomed" if is_groomed else ""
                            print(f"  ✓ Added trail: {run_name} ({run_difficulty}) - {status_str}{groomed_str} [Area: {area_name}]")
                        
                        except Exception as e:
                            print(f"  ⚠️ Error parsing trail: {e}")
                            continue
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing area: {e}")
                    continue
            
            print(f"Total trails parsed: {len(runs)}")
            return runs
            
        except Exception as e:
            print(f"❌ Error parsing runs: {e}")
            import traceback
            traceback.print_exc()
            return []


# Create scraper instance
purgatory_scraper = PurgatoryScraper()

def scrape_purgatory():
    """Main scraping function for Purgatory Resort"""
    return purgatory_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_purgatory()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_purgatory()
    print(f"Final result: {result}")

