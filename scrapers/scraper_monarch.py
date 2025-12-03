import common
import os
import time
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MonarchScraper(BaseScraper):
    """Monarch Mountain scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://skimonarch.com/conditions/")
        super().__init__("Monarch", website_url)
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Monarch website"""
        print("Starting to parse lifts...")
        lifts = []
        
        try:
            # Wait for the lifts table to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.lifts-table"))
            )
            time.sleep(2)  # Additional wait for dynamic content
            
            # Find the lifts table
            lifts_table = self.driver.find_element(By.CSS_SELECTOR, "table.lifts-table")
            
            # Find all rows in the tbody
            rows = lifts_table.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"Found {len(rows)} lift rows")
            
            for row in rows:
                try:
                    # Get lift name from the first td
                    lift_name_cell = row.find_element(By.CSS_SELECTOR, "td[data-label='Lift Name']")
                    lift_name = lift_name_cell.text.strip()
                    
                    if not lift_name:
                        continue
                    
                    # Get status from the status td
                    status_cell = row.find_element(By.CSS_SELECTOR, "td[data-label='Status']")
                    status_span = status_cell.find_element(By.TAG_NAME, "span")
                    status_text = status_span.text.strip().upper()
                    
                    # Determine if lift is open
                    # Open status has color: #48A75E and text "Open"
                    # Closed status has color: red and text "Closed"
                    is_open = "OPEN" in status_text
                    
                    # Determine lift type from name
                    lift_type = self.map_lift_type(lift_name)
                    
                    lift_obj = {
                        "liftName": lift_name,
                        "liftType": lift_type,
                        "liftStatus": is_open
                    }
                    
                    lifts.append(lift_obj)
                    print(f"  ✓ Added lift: {lift_name} ({lift_type}) - Open: {is_open}")
                    
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
    
    def map_lift_type(self, lift_name: str) -> str:
        """Map lift name to lift type"""
        name_lower = lift_name.lower()
        
        if "carpet" in name_lower or "tubing" in name_lower:
            return "Magic Carpet"
        elif "gondola" in name_lower:
            return "Gondola"
        elif "quad" in name_lower:
            return "Quad Chair"
        elif "triple" in name_lower:
            return "Triple Chair"
        elif "double" in name_lower:
            return "Double Chair"
        else:
            # Default to Chair for most lifts
            return "Chair"
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Monarch website
        
        All trail data is present in the static HTML - no need to click accordion panels.
        We find all trails-table elements and parse each one directly.
        """
        print("Starting to parse runs...")
        runs = []
        
        try:
            # Wait for at least one trails table to be present
            print("Waiting for trails tables...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.trails-table"))
            )
            time.sleep(1)  # Small wait for page to fully load
            
            # Find ALL trails-table elements on the page
            # The data is already in the static HTML - no clicking needed
            all_trails_tables = self.driver.find_elements(By.CSS_SELECTOR, "table.trails-table")
            print(f"Found {len(all_trails_tables)} trails tables on page")
            
            # Map table index to area name based on HTML structure
            # Table 0: Frontside Terrain (32 trails)
            # Table 1: Learning Areas (3 trails)
            # Table 2: Panorama Ridge (15 trails)
            # Table 3: Breezeway Terrain (10 trails)
            # Table 4: No Name Basin (12 trails)
            # Table 5: Mirkwood Basin (8 trails)
            area_names = [
                "Frontside Terrain",
                "Learning Areas", 
                "Panorama Ridge",
                "Breezeway Terrain",
                "No Name Basin",
                "Mirkwood Basin"
            ]
            
            # Parse each table
            for table_idx, trails_table in enumerate(all_trails_tables):
                area_name = area_names[table_idx] if table_idx < len(area_names) else f"Area {table_idx + 1}"
                print(f"Processing table {table_idx + 1}: {area_name}")
                self._parse_trails_table(trails_table, area_name, table_idx, runs)
            
            print(f"Total trails parsed: {len(runs)}")
            return runs
            
        except Exception as e:
            print(f"❌ Error parsing runs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_text_content(self, element) -> str:
        """Get text content from element using JavaScript (works even for hidden elements)"""
        return self.driver.execute_script("return arguments[0].textContent;", element).strip()
    
    def _parse_trails_table(self, trails_table, area_name, table_idx, runs):
        """Helper method to parse trails from a single table
        
        Uses positional cell access since the data is in static HTML.
        Cells: [0]=Trail, [1]=Difficulty, [2]=Groomed, [3]=Status
        
        Note: Uses JavaScript textContent to read hidden elements in collapsed accordions.
        """
        try:
            # Find all rows in the tbody
            rows = trails_table.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"    Found {len(rows)} trail rows in {area_name}")
            
            parsed_count = 0
            error_count = 0
            
            for row_idx, row in enumerate(rows):
                try:
                    # Get all cells in the row by position
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 4:
                        error_count += 1
                        continue
                    
                    # Cell 0: Trail name - use JavaScript to get text from hidden elements
                    trail_name = self._get_text_content(cells[0])
                    trail_name = " ".join(trail_name.split())  # Clean whitespace
                    
                    if not trail_name:
                        error_count += 1
                        continue
                    
                    # Cell 1: Difficulty (SVG icon) - attributes work even when hidden
                    try:
                        run_difficulty = self.parse_difficulty(cells[1])
                    except Exception:
                        run_difficulty = "blue1"
                    
                    # Cell 2: Groomed status (SVG checkmark)
                    try:
                        is_groomed = self.parse_groomed_status(cells[2])
                    except Exception:
                        is_groomed = False
                    
                    # Cell 3: Status (Open/Closed span) - use JavaScript for hidden text
                    try:
                        status_text = self._get_text_content(cells[3]).upper()
                        is_open = "OPEN" in status_text
                    except Exception:
                        is_open = False
                    
                    run_obj = {
                        "runName": trail_name,
                        "runStatus": is_open,
                        "runDifficulty": run_difficulty,
                        "runArea": area_name,
                        "runGroomed": is_groomed
                    }
                    
                    runs.append(run_obj)
                    parsed_count += 1
                    status_str = "Open" if is_open else "Closed"
                    groomed_str = ", Groomed" if is_groomed else ""
                    print(f"  ✓ {trail_name} ({run_difficulty}) - {status_str}{groomed_str}")
                    
                except Exception as e:
                    error_count += 1
                    if row_idx < 3:
                        print(f"  ⚠️ ERROR row {row_idx}: {e}")
                    continue
                    
            print(f"    ✓ Parsed {parsed_count} trails, {error_count} errors for {area_name}")
            
        except Exception as e:
            print(f"  ⚠️ Error parsing trails table: {e}")
            import traceback
            traceback.print_exc()
    
    def parse_difficulty(self, difficulty_cell) -> str:
        """Parse difficulty from SVG icon in the difficulty cell
        
        Monarch uses:
        - Green circle (#4CAF50) = Green/Beginner
        - Blue square (#2196F3) = Blue/Intermediate  
        - Black diamond path (#000000) = Black/Advanced
        - Orange ellipse (#FF9800) = Terrain Park
        - Image = Double Black/Expert
        """
        try:
            # Look for SVG elements
            svg_elements = difficulty_cell.find_elements(By.TAG_NAME, "svg")
            
            if not svg_elements:
                # Check for img elements (for expert-only/double black trails)
                img_elements = difficulty_cell.find_elements(By.TAG_NAME, "img")
                if img_elements:
                    return "black2"
                return "blue1"  # Default
            
            svg = svg_elements[0]
            
            # Check for SVG shape elements
            paths = svg.find_elements(By.TAG_NAME, "path")
            circles = svg.find_elements(By.TAG_NAME, "circle")
            rects = svg.find_elements(By.TAG_NAME, "rect")
            ellipses = svg.find_elements(By.TAG_NAME, "ellipse")
            
            # Green circle = green trail
            if circles:
                circle = circles[0]
                fill_color = circle.get_attribute("fill")
                if fill_color and "#4CAF50" in fill_color.upper():
                    return "green"
            
            # Blue square = blue trail
            if rects:
                rect = rects[0]
                fill_color = rect.get_attribute("fill")
                if fill_color and "#2196F3" in fill_color.upper():
                    return "blue1"
            
            # Black diamond = black trail (path with black fill)
            if paths:
                path = paths[0]
                d_attr = path.get_attribute("d")
                fill_color = path.get_attribute("fill")
                if d_attr and "L" in d_attr and fill_color and "#000000" in fill_color.upper():
                    return "black1"
            
            # Orange ellipse = Terrain Park (not double black!)
            if ellipses:
                ellipse = ellipses[0]
                fill_color = ellipse.get_attribute("fill")
                if fill_color and "#FF9800" in fill_color.upper():
                    return "terrainpark"
            
            # Default to blue if we can't determine
            return "blue1"
            
        except Exception as e:
            print(f"    Error parsing difficulty: {e}")
            return "blue1"
    
    def parse_groomed_status(self, groomed_cell) -> bool:
        """Parse groomed status from SVG checkmark"""
        try:
            # Look for SVG with checkmark (has path with "Z" at end indicating checkmark)
            svg_elements = groomed_cell.find_elements(By.TAG_NAME, "svg")
            
            if svg_elements:
                # If there's an SVG, it's likely a checkmark (groomed)
                # Check for path with "Z" which indicates a checkmark path
                svg = svg_elements[0]
                paths = svg.find_elements(By.TAG_NAME, "path")
                if paths:
                    path = paths[0]
                    d_attr = path.get_attribute("d")
                    if d_attr and "Z" in d_attr:
                        return True
            
            # If no SVG or no checkmark path, it's not groomed
            return False
            
        except Exception as e:
            print(f"    Error parsing groomed status: {e}")
            return False


# Create scraper instance
monarch_scraper = MonarchScraper()

def scrape_monarch():
    """Main scraping function for Monarch Mountain"""
    return monarch_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_monarch()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_monarch()
    print(f"Final result: {result}")

