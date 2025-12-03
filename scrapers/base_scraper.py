import common
import os
import traceback
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class BaseScraper(ABC):
    """Base scraper class with shared functionality for all resort scrapers"""
    
    def __init__(self, resort_name: str, website_url: str):
        self.resort_name = resort_name
        self.website_url = website_url
        
        # Selenium Grid configuration
        self.selenium_host = os.environ.get("SELENIUM_HOST", "selenium-hub")
        self.selenium_port = os.environ.get("SELENIUM_PORT", "4444")
        self.selenium_url = f"http://{self.selenium_host}:{self.selenium_port}/wd/hub"
        
        # Use local Chrome driver if SELENIUM_HOST is not set or set to "local"
        self.use_local_driver = os.environ.get("SELENIUM_HOST", "").lower() in ("", "local", "localhost")
        
        self.driver = None
    
    def get_chrome_options(self) -> ChromeOptions:
        """Configure Chrome options for Selenium Grid"""
        chrome_options = ChromeOptions()
        
        # Essential flags for containerized Chrome
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        
        return chrome_options
    
    def connect_to_selenium(self) -> bool:
        """Initialize connection to Selenium Grid or local Chrome driver"""
        try:
            if self.use_local_driver:
                print("Using local Chrome/Chromium driver")
                from selenium.webdriver.chrome.service import Service as ChromeService
                
                chrome_options = self.get_chrome_options()
                
                # Check for Chromium binary path (for Docker/ECS)
                chrome_bin = os.environ.get("CHROME_BIN")
                if chrome_bin:
                    chrome_options.binary_location = chrome_bin
                    print(f"Using Chrome binary: {chrome_bin}")
                
                # Check for ChromeDriver path (for Docker/ECS)
                chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
                if chromedriver_path:
                    service = ChromeService(executable_path=chromedriver_path)
                    print(f"Using ChromeDriver: {chromedriver_path}")
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # Use chromedriver from PATH
                    self.driver = webdriver.Chrome(options=chrome_options)
                
                print("Local Chrome driver initialized successfully")
            else:
                print(f"Connecting to Selenium Grid at {self.selenium_url}")
                
                chrome_options = self.get_chrome_options()
                self.driver = webdriver.Remote(
                    command_executor=self.selenium_url,
                    options=chrome_options
                )
                print("Connected to Selenium Grid successfully")
            return True
        except Exception as e:
            print(f"Failed to connect to Selenium: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_website(self) -> bool:
        """Navigate to the resort website"""
        try:
            print(f"Navigating to {self.resort_name} website...")
            self.driver.get(self.website_url)
            print("Driver connected, beginning processing")
            return True
        except Exception as e:
            print(f"Failed to navigate to website: {e}")
            return False
    
    def save_data(self, lifts: list, runs: list) -> str:
        """Save scraped data to database"""
        try:
            json_string = common.prepareAndSaveData(lifts, runs, self.resort_name.lower())
            print("Data successfully saved to database")
            return json_string
        except Exception as e:
            print(f"Failed to save data: {e}")
            raise
    
    def cleanup(self):
        """Clean up WebDriver resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("Driver closed successfully")
            except:
                print("Error closing driver (may have already been closed)")
    
    @abstractmethod
    def parse_lifts(self) -> list:
        """Parse lifts data from website - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def parse_runs(self) -> list:
        """Parse runs data from website - must be implemented by subclasses"""
        pass
    
    def scrape(self) -> dict:
        """Main scraping method that orchestrates the entire process"""
        try:
            # Connect to Selenium Grid
            if not self.connect_to_selenium():
                return {
                    "statusCode": 500,
                    "body": "Failed to connect to Selenium Grid"
                }
            
            # Navigate to website
            if not self.navigate_to_website():
                return {
                    "statusCode": 500,
                    "body": "Failed to navigate to website"
                }
            
            # Parse data using subclass implementations
            lifts = self.parse_lifts()
            runs = self.parse_runs()
            
            print(f"Successfully scraped {len(lifts)} lifts and {len(runs)} runs")
            print("Lifts:", lifts)
            print("Runs:", runs)
            
            # Save to database
            self.save_data(lifts, runs)
            
            return {
                "statusCode": 200,
                "body": f"{self.resort_name} scraping completed successfully"
            }
            
        except Exception as e:
            print("Exception occurred during scraping:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            
            return {
                "statusCode": 202,
                "body": f"Exception raised: {str(e)}"
            }
        
        finally:
            self.cleanup() 