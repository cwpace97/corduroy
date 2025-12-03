import common
import os
import time
import json
import re
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrestedButteScraper(BaseScraper):
    """Crested Butte Resort scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.skicb.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx")
        super().__init__("Crested Butte", website_url)
    
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
        """Parse lifts data from Crested Butte website"""
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
                        
                        # Status can be numeric (0=Closed, 1=Open, 2=On-Hold, 3=Scheduled)
                        # or string ("Closed", "Open", "On-Hold", "Scheduled")
                        status = lift_data.get('Status', 0)
                        is_open = self.parse_status(status)
                        
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
    
    def parse_status(self, status) -> bool:
        """Parse lift/trail status from numeric or string format"""
        if isinstance(status, int):
            # Numeric: 0=Closed, 1=Open, 2=On-Hold, 3=Scheduled
            return status in [1, 3]  # Open or Scheduled
        else:
            # String format
            status_str = str(status).lower()
            return status_str in ['open', 'scheduled']
    
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
    
    def map_difficulty(self, difficulty_level) -> str:
        """Map difficulty level to standard format"""
        # Crested Butte uses both numeric and string formats
        if isinstance(difficulty_level, int):
            # Numeric: 1=Green, 2=Blue, 3=Black, 4=Double Black, 5=Terrain Park
            difficulty_map = {
                1: 'green',
                2: 'blue1',
                3: 'black1',
                4: 'black2',
                5: 'terrainpark'
            }
            return difficulty_map.get(difficulty_level, 'blue1')
        else:
            # String format
            difficulty_str = str(difficulty_level).lower()
            if 'green' in difficulty_str or 'easiest' in difficulty_str:
                return 'green'
            elif 'blue' in difficulty_str or 'intermediate' in difficulty_str:
                return 'blue1'
            elif 'double black' in difficulty_str or 'expert' in difficulty_str:
                return 'black2'
            elif 'black' in difficulty_str or 'advanced' in difficulty_str:
                return 'black1'
            elif 'park' in difficulty_str or 'terrain' in difficulty_str:
                return 'terrainpark'
            else:
                return 'blue1'
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Crested Butte website"""
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
                        
                        # Difficulty - handle both numeric and string formats
                        difficulty_level = trail_data.get('Difficulty', 2)
                        run_difficulty = self.map_difficulty(difficulty_level)
                        
                        run_obj = {
                            "runName": run_name,
                            "runStatus": is_open,
                            "runDifficulty": run_difficulty,
                            "runArea": area_name,  # Include the area name
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
crestedbutte_scraper = CrestedButteScraper()

def scrape_crestedbutte():
    """Main scraping function for Crested Butte Resort"""
    return crestedbutte_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_crestedbutte()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_crestedbutte()
    print(f"Final result: {result}")

