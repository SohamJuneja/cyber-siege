import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import random
import time
import csv
import os
import logging
from datetime import datetime
import json
import traceback
from fake_useragent import UserAgent
import threading
import argparse
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='stealth_price_tracker.log'
)

class StealthPriceTracker:
    def __init__(self, config_file='config.json', tracking_interval_range=(30, 60), significant_change_threshold=5.0):
        """
        Initialize the stealth price tracker.
        
        Args:
            config_file (str): Path to the configuration file with product URLs
            tracking_interval_range (tuple): Range of wait times between checks in seconds
            significant_change_threshold (float): Percentage threshold for significant price changes
        """
        self.config_file = config_file
        self.tracking_interval_range = tracking_interval_range
        self.significant_change_threshold = significant_change_threshold
        self.product_history = {}  # Dictionary to store previous prices for comparison
        self.csv_filename = f"price_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.ua = UserAgent()
        self.lock = threading.Lock()  # For thread-safe CSV writing
        
        # Load configuration
        self.load_config()
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Product URL', 'Product Name', 'Price', 'Currency', 'Change (%)', 'Significant Change'])
        
        logging.info(f"Stealth price tracker initialized")
        logging.info(f"Data will be saved to: {self.csv_filename}")

    def load_config(self):
        """
        Load product URLs and other configuration from JSON file.
        Creates a default config if file doesn't exist.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                # Create default configuration
                self.config = {
                    "products": [
                        {
                            "name": "Example Walmart Product",
                            "url": "https://www.walmart.com/ip/PlayStation-5-Console-Marvel-s-Spider-Man-2-Bundle/1500394016",
                            "site": "walmart"
                        },
                        {
                            "name": "Example Best Buy Product",
                            "url": "https://www.bestbuy.com/site/sony-playstation-5-console-marvels-spider-man-2-bundle/6559233.p",
                            "site": "bestbuy"
                        }
                    ],
                    "max_retries": 3,
                    "retry_delay": 5,
                    "session_duration": 120  # Minutes before starting a new browser session
                }
                # Save default config
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=4)
            
            logging.info(f"Loaded configuration with {len(self.config['products'])} products")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            # Use a minimal default config
            self.config = {
                "products": [],
                "max_retries": 3,
                "retry_delay": 5,
                "session_duration": 120
            }

    def get_random_delay(self, min_delay=1, max_delay=3):
        """
        Get a random delay to mimic human behavior.
        
        Args:
            min_delay (float): Minimum delay in seconds
            max_delay (float): Maximum delay in seconds
            
        Returns:
            float: Random delay in seconds
        """
        return random.uniform(min_delay, max_delay)

    def human_like_scroll(self, driver):
        """
        Scroll the page in a human-like manner.
        
        Args:
            driver: Selenium WebDriver instance
        """
        scroll_pause_time = random.uniform(0.5, 2)
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Calculate a random scroll position (not too far down)
        scroll_to = random.randint(300, 1000)
        
        # Scroll down to random position in multiple small steps
        current_position = 0
        while current_position < scroll_to:
            # Scroll down in small increments
            step = random.randint(100, 300)
            current_position += step
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.1, 0.3))
        
        # Scroll back up a bit (humans do this sometimes)
        if random.random() > 0.7:  # 30% chance to scroll back up
            up_scroll = random.randint(50, 200)
            driver.execute_script(f"window.scrollTo(0, {current_position - up_scroll});")
            time.sleep(random.uniform(0.1, 0.3))

    def init_driver(self):
        """
        Initialize an undetected Chrome driver with randomized settings.
        
        Returns:
            WebDriver: Initialized browser instance
        """
        try:
            options = uc.ChromeOptions()
            
            # Randomize window size (within normal ranges)
            width = random.randint(1200, 1600)
            height = random.randint(800, 1000)
            
            # Set a random user agent
            user_agent = self.ua.random
            options.add_argument(f'user-agent={user_agent}')
            
            # Random window size
            options.add_argument(f"--window-size={width},{height}")
            
            # Disable automation flags
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Add some random arguments that real browsers might have
            if random.random() > 0.5:
                options.add_argument("--disable-notifications")
            if random.random() > 0.7:
                options.add_argument("--disable-popup-blocking")
            
            # Initialize the undetected ChromeDriver
            driver = uc.Chrome(options=options)
            
            # Additional settings to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Add random cookies to seem more like a returning visitor
            driver.get("https://www.google.com")  # Navigate to a site first
            time.sleep(self.get_random_delay(0.5, 1.5))
            
            # Set random cookies
            cookies = [
                {"name": f"session_cookie_{random.randint(100, 999)}", "value": f"{random.randint(10000, 99999)}"},
                {"name": "returning_visitor", "value": "true"},
                {"name": f"last_visit", "value": f"{int(time.time() - random.randint(86400, 604800))}"}
            ]
            
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass  # Ignore if cookies can't be set
                    
            return driver
        except Exception as e:
            logging.error(f"Error initializing driver: {e}")
            traceback.print_exc()
            return None

    def handle_captcha(self, driver):
        """
        Attempt to detect and handle CAPTCHA challenges.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if CAPTCHA was bypassed or not present, False otherwise
        """
        try:
            # Common CAPTCHA detection patterns
            captcha_indicators = [
                # Common text indicators
                "//h1[contains(text(), 'Robot') or contains(text(), 'captcha') or contains(text(), 'Verify')]",
                "//div[contains(text(), 'Robot') or contains(text(), 'captcha') or contains(text(), 'Verify')]",
                "//p[contains(text(), 'Robot') or contains(text(), 'captcha') or contains(text(), 'Verify')]",
                # Common reCAPTCHA elements
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[@class='g-recaptcha']",
                # Common CAPTCHA image elements
                "//img[contains(@src, 'captcha')]",
            ]
            
            for indicator in captcha_indicators:
                try:
                    if driver.find_elements(By.XPATH, indicator):
                        logging.warning("CAPTCHA detected. Attempting to handle...")
                        
                        # Strategy 1: Wait for a while to appear more human-like
                        time.sleep(self.get_random_delay(5, 10))
                        
                        # Strategy 2: Refresh the page
                        driver.refresh()
                        time.sleep(self.get_random_delay(3, 7))
                        
                        # Check if CAPTCHA is still present
                        if not driver.find_elements(By.XPATH, indicator):
                            logging.info("CAPTCHA appears to be bypassed after refresh")
                            return True
                            
                        # Strategy 3: Try a new session
                        logging.info("CAPTCHA still present. Will retry with new session.")
                        return False
                except:
                    continue
                    
            # No CAPTCHA detected
            return True
            
        except Exception as e:
            logging.error(f"Error in CAPTCHA handling: {e}")
            return False

    def extract_price_walmart(self, driver):
        """
        Extract product name and price from Walmart product page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            tuple: (product_name, price, currency) or (None, None, None) if extraction fails
        """
        try:
            # Wait for the product information to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='price-wrap']"))
            )
            
            # Extract product name
            try:
                product_name_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
                product_name = product_name_elem.text.strip()
            except:
                product_name = "Unknown Walmart Product"
            
            # Extract price
            try:
                price_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='price-wrap'] span"))
                )
                price_text = price_elem.text.strip()
                
                # Extract numeric price and currency
                price_match = re.search(r'[$€£¥](\d+(?:\.\d+)?)', price_text)
                if price_match:
                    currency = price_text[0]  # First character should be the currency symbol
                    price = float(price_match.group(1))
                    return product_name, price, currency
            except:
                pass
                
            # Secondary attempt if the first method fails
            try:
                # Try different selectors as fallbacks
                price_elems = driver.find_elements(By.XPATH, "//*[contains(@class, 'price') or contains(@id, 'price')]")
                for elem in price_elems:
                    price_text = elem.text.strip()
                    price_match = re.search(r'[$€£¥](\d+(?:\.\d+)?)', price_text)
                    if price_match:
                        currency = price_text[0]  # First character should be the currency symbol
                        price = float(price_match.group(1))
                        return product_name, price, currency
            except:
                pass
                
            logging.warning(f"Could not extract price from Walmart page")
            return product_name, None, None
            
        except Exception as e:
            logging.error(f"Error extracting data from Walmart: {e}")
            return None, None, None

    def extract_price_bestbuy(self, driver):
        """
        Extract product name and price from Best Buy product page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            tuple: (product_name, price, currency) or (None, None, None) if extraction fails
        """
        try:
            # Wait for the product information to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "priceView-customer-price"))
            )
            
            # Extract product name
            try:
                product_name_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "heading-5"))
                )
                product_name = product_name_elem.text.strip()
            except:
                product_name = "Unknown Best Buy Product"
            
            # Extract price
            try:
                price_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "priceView-customer-price"))
                )
                price_text = price_elem.text.strip()
                
                # Extract numeric price and currency
                price_match = re.search(r'[$€£¥](\d+(?:\.\d+)?)', price_text)
                if price_match:
                    currency = price_text[0]  # First character should be the currency symbol
                    price = float(price_match.group(1))
                    return product_name, price, currency
            except:
                pass
                
            # Secondary attempt if the first method fails
            try:
                # Try different selectors as fallbacks
                price_elems = driver.find_elements(By.XPATH, "//*[contains(@class, 'price') or contains(@id, 'price')]")
                for elem in price_elems:
                    price_text = elem.text.strip()
                    price_match = re.search(r'[$€£¥](\d+(?:\.\d+)?)', price_text)
                    if price_match:
                        currency = price_text[0]  # First character should be the currency symbol
                        price = float(price_match.group(1))
                        return product_name, price, currency
            except:
                pass
                
            logging.warning(f"Could not extract price from Best Buy page")
            return product_name, None, None
            
        except Exception as e:
            logging.error(f"Error extracting data from Best Buy: {e}")
            return None, None, None

    def extract_product_data(self, driver, site):
        """
        Extract product information based on site type.
        
        Args:
            driver: Selenium WebDriver instance
            site: Site identifier ('walmart' or 'bestbuy')
            
        Returns:
            tuple: (product_name, price, currency) or (None, None, None) if extraction fails
        """
        if site.lower() == 'walmart':
            return self.extract_price_walmart(driver)
        elif site.lower() == 'bestbuy':
            return self.extract_price_bestbuy(driver)
        else:
            # Generic extraction for other sites
            try:
                # Wait for the page to load
                time.sleep(self.get_random_delay(3, 5))
                
                # Extract product name
                title_elem = driver.find_element(By.TAG_NAME, "h1")
                product_name = title_elem.text.strip() if title_elem else "Unknown Product"
                
                # Look for price elements using common patterns
                price_patterns = [
                    "//span[contains(@class, 'price')]",
                    "//div[contains(@class, 'price')]",
                    "//span[contains(@id, 'price')]",
                    "//div[contains(@id, 'price')]",
                    "//span[contains(text(), '$')]",
                    "//div[contains(text(), '$')]"
                ]
                
                for pattern in price_patterns:
                    elems = driver.find_elements(By.XPATH, pattern)
                    for elem in elems:
                        price_text = elem.text.strip()
                        price_match = re.search(r'[$€£¥](\d+(?:\.\d+)?)', price_text)
                        if price_match:
                            currency = price_text[0]  # First character should be the currency symbol
                            price = float(price_match.group(1))
                            return product_name, price, currency
                
                logging.warning(f"Could not extract price using generic extractor")
                return product_name, None, None
                
            except Exception as e:
                logging.error(f"Error in generic price extraction: {e}")
                return None, None, None

    def calculate_price_change(self, product_url, current_price):
        """
        Calculate the percentage change in price compared to the last recorded price.
        
        Args:
            product_url (str): URL of the product
            current_price (float): The current price of the product
            
        Returns:
            tuple: (percentage_change, is_significant_change)
        """
        if product_url not in self.product_history or self.product_history[product_url] == 0:
            return 0.0, False
        
        previous_price = self.product_history[product_url]
        price_change = ((current_price - previous_price) / previous_price) * 100
        
        is_significant = abs(price_change) >= self.significant_change_threshold
        
        return round(price_change, 2), is_significant

    def record_price(self, product_url, product_name, price, currency, price_change=0.0, is_significant=False):
        """
        Record the price data to the CSV file.
        
        Args:
            product_url (str): URL of the product
            product_name (str): The name of the product
            price (float): The current price of the product
            currency (str): The currency of the price
            price_change (float): The percentage change in price
            is_significant (bool): Whether the price change is significant
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with self.lock:  # Thread-safe writing
            with open(self.csv_filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, product_url, product_name, price, currency, price_change, is_significant])
        
        # Update the product history
        self.product_history[product_url] = price

    def track_product(self, product):
        """
        Track a single product's price.
        
        Args:
            product (dict): Product information including URL and site
        """
        url = product.get('url')
        site = product.get('site')
        
        if not url or not site:
            logging.error(f"Invalid product configuration: {product}")
            return
        
        retries = 0
        max_retries = self.config.get('max_retries', 3)
        
        while retries < max_retries:
            driver = None
            try:
                # Initialize a new driver
                driver = self.init_driver()
                if not driver:
                    logging.error("Failed to initialize driver, retrying...")
                    retries += 1
                    continue
                
                # Add random delay before navigation
                time.sleep(self.get_random_delay(1, 3))
                
                # Navigate to the product page
                logging.info(f"Navigating to {url}")
                driver.get(url)
                
                # Add random delay to simulate page loading time
                time.sleep(self.get_random_delay(2, 5))
                
                # Check for CAPTCHA
                if not self.handle_captcha(driver):
                    logging.warning(f"CAPTCHA handling failed for {url}, retrying...")
                    retries += 1
                    if driver:
                        driver.quit()
                    time.sleep(self.config.get('retry_delay', 5))
                    continue
                
                # Perform human-like scrolling
                self.human_like_scroll(driver)
                
                # Extract product data
                product_name, price, currency = self.extract_product_data(driver, site)
                
                # Close the driver
                driver.quit()
                driver = None
                
                # Skip if we couldn't extract price
                if price is None:
                    logging.warning(f"Failed to extract price for {url}, retrying...")
                    retries += 1
                    time.sleep(self.config.get('retry_delay', 5))
                    continue
                
                # Calculate price change
                price_change, is_significant = self.calculate_price_change(url, price)
                
                # Skip recording if price hasn't changed and this isn't the first record
                if url in self.product_history and price == self.product_history[url]:
                    logging.info(f"No price change for {url}, skipping record")
                    return
                
                # Record the price
                self.record_price(url, product_name, price, currency, price_change, is_significant)
                
                if is_significant:
                    logging.warning(f"Significant price change detected for {product_name}: {price_change}%")
                else:
                    logging.info(f"Recorded price for {product_name}: {price} {currency}")
                
                # Success, so break the retry loop
                break
                
            except Exception as e:
                logging.error(f"Error tracking product {url}: {e}")
                traceback.print_exc()
                retries += 1
            finally:
                # Ensure driver is closed
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            
            # Wait before retrying
            if retries < max_retries:
                retry_delay = self.config.get('retry_delay', 5)
                time.sleep(retry_delay)

    def track_prices(self, duration_minutes=60):
        """
        Track prices for all products over a specified duration.
        
        Args:
            duration_minutes (int): The duration to track prices in minutes
        """
        end_time = time.time() + (duration_minutes * 60)
        iterations = 0
        
        logging.info(f"Starting price tracking for {duration_minutes} minutes")
        
        while time.time() < end_time:
            iterations += 1
            logging.info(f"Iteration {iterations} started")
            
            # Process each product in sequence
            for product in self.config['products']:
                # Check if we're still within the duration
                if time.time() >= end_time:
                    break
                    
                self.track_product(product)
                
                # Random delay between product checks to mimic human behavior
                if time.time() < end_time:
                    interval = random.randint(self.tracking_interval_range[0], self.tracking_interval_range[1])
                    logging.info(f"Waiting {interval} seconds until next product check.")
                    time.sleep(interval)
            
            # Check if we're still within the duration
            if time.time() >= end_time:
                break
                
            # Random delay between iterations
            if time.time() < end_time:
                interval = random.randint(self.tracking_interval_range[0], self.tracking_interval_range[1])
                logging.info(f"Iteration {iterations} completed. Waiting {interval} seconds until next iteration.")
                time.sleep(interval)
        
        logging.info("Price tracking completed")

    def analyze_price_history(self):
        """
        Analyze the collected price history and print summary statistics.
        """
        products_tracked = set()
        price_changes = {}
        
        with open(self.csv_filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                product_url = row['Product URL']
                products_tracked.add(product_url)
                
                if product_url not in price_changes:
                    price_changes[product_url] = []
                
                try:
                    change = float(row['Change (%)'])
                    price_changes[product_url].append(change)
                except (ValueError, TypeError):
                    continue
        
        # Print analysis results
        print("\n===== PRICE ANALYSIS SUMMARY =====")
        print(f"Total products tracked: {len(products_tracked)}")
        
        for product_url, changes in price_changes.items():
            if not changes:
                continue
                
            significant_changes = [c for c in changes if abs(c) >= self.significant_change_threshold]
            
            # Find product name from the URL
            product_name = "Unknown"
            for product in self.config['products']:
                if product.get('url') == product_url:
                    product_name = product.get('name', product_url)
                    break
            
            print(f"\nProduct: {product_name}")
            print(f"  URL: {product_url}")
            print(f"  Total price records: {len(changes)}")
            print(f"  Significant price changes: {len(significant_changes)}")
            
            if changes:
                print(f"  Max increase: {max(changes):.2f}%")
                print(f"  Max decrease: {min(changes):.2f}%")
                print(f"  Average change: {sum(changes)/len(changes):.2f}%")
        
        print("\nFull price history saved to:", self.csv_filename)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Stealth e-commerce price tracker')
    parser.add_argument('--config', type=str, default='config.json', help='Path to configuration file')
    parser.add_argument('--duration', type=int, default=60, help='Duration to track prices in minutes')
    parser.add_argument('--interval-min', type=int, default=30, help='Minimum interval between checks in seconds')
    parser.add_argument('--interval-max', type=int, default=60, help='Maximum interval between checks in seconds')
    parser.add_argument('--threshold', type=float, default=5.0, help='Threshold for significant price changes in percentage')
    return parser.parse_args()

def main():
    """
    Main function to run the price tracker.
    """
    args = parse_arguments()
    
    # Create and run the price tracker
    tracker = StealthPriceTracker(
        config_file=args.config,
        tracking_interval_range=(args.interval_min, args.interval_max),
        significant_change_threshold=args.threshold
    )
    
    try:
        tracker.track_prices(duration_minutes=args.duration)
        tracker.analyze_price_history()
    except KeyboardInterrupt:
        print("Price tracking stopped by user")
        tracker.analyze_price_history()
    except Exception as e:
        logging.critical(f"Fatal error in price tracker: {e}")
        traceback.print_exc()
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()