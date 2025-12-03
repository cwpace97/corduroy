#!/usr/bin/env python3
"""
Orchestrator script to run all resort scrapers sequentially.
Designed for ECS Fargate tasks - runs all scrapers in a single container.
"""

import os
import sys
import traceback
from pathlib import Path

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all scrapers
from scraper_abasin import handler as scrape_abasin
from scraper_copper import handler as scrape_copper
from scraper_loveland import handler as scrape_loveland
from scraper_winterpark import handler as scrape_winterpark
from scraper_keystone import handler as scrape_keystone
from scraper_breckenridge import handler as scrape_breckenridge
from scraper_vail import handler as scrape_vail
from scraper_steamboat import handler as scrape_steamboat
from scraper_crestedbutte import handler as scrape_crestedbutte
from scraper_purgatory import handler as scrape_purgatory
from scraper_telluride import handler as scrape_telluride
from scraper_monarch import handler as scrape_monarch

# Mapping of scraper names to handler functions
SCRAPERS = [
    ("Arapahoe Basin", scrape_abasin),
    ("Copper Mountain", scrape_copper),
    ("Loveland", scrape_loveland),
    ("Winter Park", scrape_winterpark),
    ("Keystone", scrape_keystone),
    ("Breckenridge", scrape_breckenridge),
    ("Vail", scrape_vail),
    ("Steamboat", scrape_steamboat),
    ("Crested Butte", scrape_crestedbutte),
    ("Purgatory", scrape_purgatory),
    ("Telluride", scrape_telluride),
    ("Monarch", scrape_monarch),
]


def run_all_scrapers():
    """Run all scrapers sequentially"""
    print("=" * 60)
    print("Starting Resort Scraper Job")
    print("=" * 60)
    print(f"Total scrapers: {len(SCRAPERS)}")
    print()
    
    # Set environment variable to use local Chrome driver
    os.environ["SELENIUM_HOST"] = "local"
    
    success_count = 0
    failure_count = 0
    failed_scrapers = []
    
    for resort_name, scraper_func in SCRAPERS:
        print("-" * 60)
        print(f"Scraping {resort_name}...")
        print("-" * 60)
        
        try:
            result = scraper_func()
            
            # Check if result indicates success
            if isinstance(result, dict):
                status_code = result.get("statusCode", 200)
                if status_code == 200:
                    print(f"✅ {resort_name} completed successfully")
                    success_count += 1
                else:
                    print(f"⚠️  {resort_name} completed with status code {status_code}")
                    failure_count += 1
                    failed_scrapers.append(resort_name)
            else:
                print(f"✅ {resort_name} completed")
                success_count += 1
                
        except Exception as e:
            print(f"❌ {resort_name} failed: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            failure_count += 1
            failed_scrapers.append(resort_name)
        
        print()
    
    # Summary
    print("=" * 60)
    print("Scraping Summary")
    print("=" * 60)
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    
    if failed_scrapers:
        print(f"Failed scrapers: {', '.join(failed_scrapers)}")
    
    # Exit with error code if any scrapers failed
    if failure_count > 0:
        sys.exit(1)
    
    print("✅ All scrapers completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    run_all_scrapers()

