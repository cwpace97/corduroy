import common
import os
import time
import json
import re
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class KeystoneScraper(BaseScraper):
    """Keystone Resort scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.keystoneresort.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx")
        super().__init__("Keystone", website_url)
    
    def extract_json_data(self):
        """Extract the terrain status JSON data from the page"""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Get page source and extract the FR.TerrainStatusFeed JSON object
            page_source = self.driver.page_source
            
            # Find the JavaScript variable with the data
            pattern = r'FR\.TerrainStatusFeed\s*=\s*(\{.*?\});'
            match = re.search(pattern, page_source, re.DOTALL)
            
            if not match:
                print("❌ Could not find FR.TerrainStatusFeed in page source")
                return None
            
            json_str = match.group(1)
            data = json.loads(json_str)
            
            print(f"✓ Successfully extracted terrain data")
            return data
            
        except Exception as e:
            print(f"❌ Error extracting JSON data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Keystone website"""
        print("Starting to parse lifts...")
        
        try:
            data = self.extract_json_data()
            if not data:
                return []
            
            lifts = []
            
            # Iterate through all grooming areas
            for area in data.get('GroomingAreas', []):
                area_name = area.get('Name', 'Unknown')
                area_lifts = area.get('Lifts', [])
                
                print(f"Processing area: {area_name} ({len(area_lifts)} lifts)")
                
                for lift_data in area_lifts:
                    try:
                        lift_name = lift_data.get('Name', '')
                        if not lift_name:
                            continue
                        
                        # Status: 0=Closed, 3=Open, based on the data
                        # Statuses: 0=Closed, 1=Open, 2=On-Hold, 3=Scheduled
                        status = lift_data.get('Status', 0)
                        is_open = status in [1, 3]  # Open or Scheduled
                        
                        # Lift type
                        lift_type_raw = lift_data.get('Type', 'unknown')
                        lift_type = self.map_lift_type(lift_type_raw)
                        
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
    
    def map_lift_type(self, raw_type: str) -> str:
        """Map lift type from API to standard format"""
        type_map = {
            'gondola': 'Gondola',
            'six': 'Six-Person Chair',
            'quad': 'Quad Chair',
            'triple': 'Triple Chair',
            'double': 'Double Chair',
            'conveyor': 'Magic Carpet'
        }
        return type_map.get(raw_type.lower(), 'Chair')
    
    def map_difficulty(self, difficulty_level: int) -> str:
        """Map difficulty level to standard format"""
        # Based on the data: 1=Green, 2=Blue, 3=Black, 4=Double Black, 5=Terrain Park
        difficulty_map = {
            1: 'green',
            2: 'blue1',
            3: 'black1',
            4: 'black2',
            5: 'park'
        }
        return difficulty_map.get(difficulty_level, 'blue1')
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Keystone website"""
        print("Starting to parse runs...")
        
        try:
            data = self.extract_json_data()
            if not data:
                return []
            
            runs = []
            
            # Iterate through all grooming areas
            for area in data.get('GroomingAreas', []):
                area_name = area.get('Name', 'Unknown')
                area_trails = area.get('Trails', [])
                
                print(f"Processing area: {area_name} ({len(area_trails)} trails)")
                
                for trail_data in area_trails:
                    try:
                        run_name = trail_data.get('Name', '')
                        if not run_name:
                            continue
                        
                        # Status
                        is_open = trail_data.get('IsOpen', False)
                        is_groomed = trail_data.get('IsGroomed', False)
                        
                        # Difficulty
                        difficulty_level = trail_data.get('Difficulty', 2)
                        run_difficulty = self.map_difficulty(difficulty_level)
                        
                        run_obj = {
                            "runName": run_name,
                            "runStatus": is_open,
                            "runDifficulty": run_difficulty,
                            "runArea": area_name,  # Include the area name as requested
                            "runGroomed": is_groomed
                        }
                        
                        runs.append(run_obj)
                        status_str = "Open" if is_open else "Closed"
                        groomed_str = ", Groomed" if is_groomed else ""
                        print(f"  ✓ Added trail: {run_name} ({run_difficulty}) - {status_str}{groomed_str} [Area: {area_name}]")
                    
                    except Exception as e:
                        print(f"  ⚠️ Error parsing trail: {e}")
                        continue
            
            print(f"Total trails parsed: {len(runs)}")
            return runs
            
        except Exception as e:
            print(f"❌ Error parsing runs: {e}")
            import traceback
            traceback.print_exc()
            return []


# Create scraper instance
keystone_scraper = KeystoneScraper()

def scrape_keystone():
    """Main scraping function for Keystone Resort"""
    return keystone_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_keystone()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_keystone()
    print(f"Final result: {result}")

