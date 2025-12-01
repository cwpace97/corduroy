import common
import os
import time
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class TellurideScraper(BaseScraper):
    """Telluride Ski Resort scraper - parses lift and trail data from HTML"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://tellurideskiresort.com/snow-report/")
        super().__init__("Telluride", website_url)
    
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
        """Parse lifts data from Telluride website HTML"""
        print("Starting to parse lifts...")
        
        try:
            soup = self.get_page_soup()
            if not soup:
                return []
            
            lifts = []
            
            # Find the lifts table
            lift_table = soup.find('table', {'id': 'tsr-report-app-lift-table'})
            if not lift_table:
                print("❌ Could not find lift table")
                return []
            
            # Find tbody and all rows
            tbody = lift_table.find('tbody')
            if not tbody:
                print("❌ Could not find lift table tbody")
                return []
            
            rows = tbody.find_all('tr')
            print(f"Found {len(rows)} lift rows")
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue
                    
                    # First cell has status icon
                    status_cell = cells[0]
                    status_icon = status_cell.find('span')
                    is_open = False
                    if status_icon:
                        icon_class = status_icon.get('class', [])
                        is_open = 'tsr-report-app-icon-open' in icon_class
                    
                    # Second cell has lift name
                    lift_name = cells[1].get_text(strip=True)
                    if not lift_name:
                        continue
                    
                    # Third cell has area (we can use this for context)
                    area = cells[2].get_text(strip=True)
                    
                    # Determine lift type from name
                    lift_type = self.extract_lift_type(lift_name)
                    
                    lift_obj = {
                        "liftName": lift_name,
                        "liftType": lift_type,
                        "liftStatus": is_open
                    }
                    
                    lifts.append(lift_obj)
                    print(f"  ✓ Added lift: {lift_name} ({lift_type}) - Open: {is_open} [Area: {area}]")
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing lift row: {e}")
                    continue
            
            print(f"Total lifts parsed: {len(lifts)}")
            return lifts
            
        except Exception as e:
            print(f"❌ Error parsing lifts: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_lift_type(self, lift_name: str) -> str:
        """Extract lift type from the lift name"""
        name_lower = lift_name.lower()
        
        if 'gondola' in name_lower or 'chondola' in name_lower:
            return 'Gondola'
        elif 'magic carpet' in name_lower or 'carpet' in name_lower:
            return 'Magic Carpet'
        elif 'express' in name_lower:
            return 'Quad Chair'  # Express lifts are typically high-speed quads
        elif 'lift' in name_lower:
            return 'Chair'
        else:
            return 'Chair'
    
    def map_difficulty(self, level: str) -> str:
        """Map trail difficulty level to standard format"""
        level_map = {
            'novice': 'green',
            'advanced_novice': 'green',  # Green-blue
            'intermediate': 'blue1',
            'advanced_intermediate': 'blue1',  # Blue-black
            'expert': 'black1',
            'extreme': 'black2'
        }
        return level_map.get(level, 'blue1')
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Telluride website HTML"""
        print("Starting to parse runs...")
        
        try:
            soup = self.get_page_soup()
            if not soup:
                return []
            
            runs = []
            
            # Find the trail list container
            trail_list = soup.find('div', class_='tsr-report-app-trail-list')
            if not trail_list:
                print("❌ Could not find trail list")
                return []
            
            # Find all lift sections (trails are grouped by lift)
            lift_sections = trail_list.find_all('div', class_='tsr-report-app-trail-list-lift')
            print(f"Found {len(lift_sections)} lift sections with trails")
            
            for section in lift_sections:
                try:
                    # Get the lift name for this section (used as area)
                    lift_header = section.find('h4')
                    area_name = 'Unknown'
                    if lift_header:
                        # Get just the text, not the status icon
                        area_name = lift_header.get_text(strip=True)
                        # Remove any trailing status text
                        area_name = area_name.strip()
                    
                    # Find all trails in this section
                    trail_container = section.find('div', class_='tsr-report-app-trail-list-trails')
                    if not trail_container:
                        continue
                    
                    trail_items = trail_container.find_all('p', class_='tsr-report-app-trail-list-trail')
                    print(f"Processing area: {area_name} ({len(trail_items)} trails)")
                    
                    for trail in trail_items:
                        try:
                            # Get data attributes
                            level = trail.get('data-level', 'intermediate')
                            is_groomed = trail.get('data-groomed', '0') == '1'
                            is_closed = trail.get('data-closed', '1') == '1'
                            is_hold = trail.get('data-hold', '0') == '1'
                            
                            # Trail is open if not closed and not on hold
                            is_open = not is_closed and not is_hold
                            
                            # Get trail name from second span
                            spans = trail.find_all('span')
                            run_name = ''
                            if len(spans) >= 2:
                                run_name = spans[1].get_text(strip=True)
                            
                            if not run_name:
                                continue
                            
                            # Map difficulty
                            run_difficulty = self.map_difficulty(level)
                            
                            run_obj = {
                                "runName": run_name,
                                "runStatus": is_open,
                                "runDifficulty": run_difficulty,
                                "runArea": area_name,
                                "runGroomed": is_groomed
                            }
                            
                            runs.append(run_obj)
                            status_str = "Open" if is_open else ("Hold" if is_hold else "Closed")
                            groomed_str = ", Groomed" if is_groomed else ""
                            print(f"  ✓ Added trail: {run_name} ({run_difficulty}) - {status_str}{groomed_str} [Area: {area_name}]")
                        
                        except Exception as e:
                            print(f"  ⚠️ Error parsing trail: {e}")
                            continue
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing lift section: {e}")
                    continue
            
            print(f"Total trails parsed: {len(runs)}")
            return runs
            
        except Exception as e:
            print(f"❌ Error parsing runs: {e}")
            import traceback
            traceback.print_exc()
            return []


# Create scraper instance
telluride_scraper = TellurideScraper()

def scrape_telluride():
    """Main scraping function for Telluride Ski Resort"""
    return telluride_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_telluride()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_telluride()
    print(f"Final result: {result}")

