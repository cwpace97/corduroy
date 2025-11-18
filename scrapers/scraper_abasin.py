import common
import os
import time
from base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ArapahoeBasinScraper(BaseScraper):
    """Arapahoe Basin Resort scraper"""
    
    def __init__(self):
        website_url = os.environ.get("WEBSITE_URL", "https://www.arapahoebasin.com/snow-report/")
        super().__init__("ArapahoeBasin", website_url)
    
    def expand_all_terrain_sections(self):
        """Click on all clickable terrain sections to expand trail lists"""
        try:
            print("Expanding terrain sections...")
            time.sleep(3)  # Wait for initial page load
            
            # Find all clickable terrain section elements
            clickable_sections = self.driver.find_elements(By.CSS_SELECTOR, ".clickable-row.second-level")
            print(f"Found {len(clickable_sections)} clickable terrain sections")
            
            for i, section in enumerate(clickable_sections):
                try:
                    section_text = section.text.strip().split('\n')[0] if section.text else f"Section {i+1}"
                    print(f"  Expanding: {section_text}")
                    
                    # Use JavaScript click to avoid interception issues
                    self.driver.execute_script("arguments[0].click();", section)
                    time.sleep(0.5)  # Small delay between clicks
                    
                except Exception as e:
                    print(f"  Error expanding section {i+1}: {e}")
                    continue
            
            # Wait for all sections to fully expand
            time.sleep(2)
            print("✓ All terrain sections expanded")
            
        except Exception as e:
            print(f"⚠️ Error expanding terrain sections: {e}")
    
    def parse_lifts(self) -> list:
        """Parse lifts data from Arapahoe Basin website"""
        print("Starting to parse lifts...")
        
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            lifts = []
            
            # Find all lift elements - they contain "(Lift)" in their text
            # and are within span elements with class "d-flex align-items-center"
            lift_spans = self.driver.find_elements(By.CSS_SELECTOR, "span.d-flex.align-items-center")
            print(f"Found {len(lift_spans)} potential lift elements")
            
            for span in lift_spans:
                try:
                    text = span.text.strip()
                    
                    # Check if this is a lift element
                    if "(Lift)" not in text:
                        continue
                    
                    # Extract lift name (remove "(Lift)" suffix)
                    lift_name = text.replace("(Lift)", "").strip()
                    
                    if not lift_name or len(lift_name) < 3:
                        continue
                    
                    # Get status from image
                    status_img = span.find_elements(By.TAG_NAME, "img")
                    is_open = False
                    
                    for img in status_img:
                        src = img.get_attribute("src") or ""
                        if "/img/sr/open.svg" in src:
                            is_open = True
                            break
                        elif "/img/sr/closed.svg" in src or "/img/sr/onhold.svg" in src:
                            is_open = False
                            break
                    
                    # Determine lift type based on name
                    lift_type = "Unknown"
                    name_lower = lift_name.lower()
                    if "express" in name_lower:
                        lift_type = "High-Speed Chair"
                    elif "carpet" in name_lower or "magic" in name_lower:
                        lift_type = "Magic Carpet"
                    elif "tow" in name_lower or "t-bar" in name_lower:
                        lift_type = "Tow"
                    else:
                        lift_type = "Chair"
                    
                    lift_obj = {
                        "liftName": lift_name,
                        "liftType": lift_type,
                        "liftStatus": is_open
                    }
                    
                    # Avoid duplicates
                    if not any(l['liftName'] == lift_name for l in lifts):
                        lifts.append(lift_obj)
                        print(f"  ✓ Added lift: {lift_name} ({lift_type}) - Open: {is_open}")
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing lift element: {e}")
                    continue
            
            print(f"Total lifts parsed: {len(lifts)}")
            return lifts
            
        except Exception as e:
            print(f"❌ Error parsing lifts: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def parse_runs(self) -> list:
        """Parse runs/trails data from Arapahoe Basin website"""
        print("Starting to parse runs...")
        
        try:
            # First expand all terrain sections to reveal all trails
            self.expand_all_terrain_sections()
            
            runs = []
            
            # Find all trail elements - they are li elements with class "secondary-option"
            # that don't have the "clickable-row" class (those are section headers)
            trail_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.secondary-option:not(.clickable-row)")
            print(f"Found {len(trail_elements)} potential trail elements")
            
            for trail in trail_elements:
                try:
                    # Get trail name
                    run_name = trail.text.strip()
                    
                    # Skip empty or very long text (likely not a trail name)
                    if not run_name or len(run_name) < 2 or len(run_name) > 50:
                        continue
                    
                    # Skip section headers or non-trail text
                    skip_keywords = ['open', 'closed', 'terrain', 'lift', 'ticket', 'pass', 'parking']
                    if any(keyword in run_name.lower() for keyword in skip_keywords):
                        continue
                    
                    # Get status and difficulty from images
                    imgs = trail.find_elements(By.TAG_NAME, "img")
                    is_open = False
                    run_difficulty = "Unknown"
                    
                    for img in imgs:
                        src = img.get_attribute("src") or ""
                        
                        # Check status
                        if "/img/sr/open.svg" in src:
                            is_open = True
                        elif "/img/sr/closed.svg" in src:
                            is_open = False
                        elif "/img/sr/inprogress.svg" in src:
                            is_open = True  # Treat in-progress as open
                        
                        # Check difficulty
                        if "/img/sr/easy.svg" in src:
                            run_difficulty = "green"
                        elif "/img/sr/intermediate.svg" in src:
                            run_difficulty = "blue1"
                        elif "/img/sr/advance.svg" in src:
                            run_difficulty = "black1"
                        elif "/img/sr/expert.svg" in src:
                            run_difficulty = "black2"
                    
                    # If no difficulty found from image, try to infer from section context
                    if run_difficulty == "Unknown":
                        try:
                            # Find the parent section header (clickable-row) to infer difficulty
                            parent = trail.find_element(By.XPATH, "./ancestor::div[contains(@class, 'clickable-row')][1]")
                            parent_text = parent.text.lower()
                            
                            # Section names often indicate difficulty
                            if "green" in parent_text or "easiest" in parent_text:
                                run_difficulty = "green"
                            elif "blue" in parent_text or "intermediate" in parent_text:
                                run_difficulty = "blue1"
                            elif "black" in parent_text or "double black" in parent_text:
                                run_difficulty = "black2"
                            elif any(word in parent_text for word in ["advanced", "expert", "steep", "chute", "cornice", "wall", "gully", "alley"]):
                                run_difficulty = "black1"
                        except:
                            pass
                        
                        # If still unknown, default to intermediate
                        if run_difficulty == "Unknown":
                            run_difficulty = "blue1"
                    
                    run_obj = {
                        "runName": run_name,
                        "runStatus": is_open,
                        "runDifficulty": run_difficulty
                    }
                    
                    # Avoid duplicates
                    if not any(r['runName'] == run_name for r in runs):
                        runs.append(run_obj)
                        print(f"  ✓ Added trail: {run_name} ({run_difficulty}) - Open: {is_open}")
                
                except Exception as e:
                    print(f"  ⚠️ Error parsing trail element: {e}")
                    continue
            
            print(f"Total trails parsed: {len(runs)}")
            return runs
            
        except Exception as e:
            print(f"❌ Error parsing runs: {e}")
            import traceback
            traceback.print_exc()
            return []


# Create scraper instance
arapahoebasin_scraper = ArapahoeBasinScraper()

def scrape_arapahoebasin():
    """Main scraping function for Arapahoe Basin Resort"""
    return arapahoebasin_scraper.scrape()

def handler(event=None, context=None):
    """Handler function for backward compatibility"""
    return scrape_arapahoebasin()

if __name__ == "__main__":
    # Run scraper directly when called as script
    result = scrape_arapahoebasin()
    print(f"Final result: {result}")
