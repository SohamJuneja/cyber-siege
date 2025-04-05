import requests
import json
import csv
import time
import os
from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='price_tracker.log'
)

class PriceTracker:
    def __init__(self, base_url, tracking_interval=300, significant_change_threshold=5.0):
        """
        Initialize the price tracker.
        
        Args:
            base_url (str): The base URL of the e-commerce API
            tracking_interval (int): Time between price checks in seconds (default: 5 minutes)
            significant_change_threshold (float): Percentage threshold for significant price changes
        """
        self.base_url = base_url
        self.tracking_interval = tracking_interval
        self.significant_change_threshold = significant_change_threshold
        self.product_history = {}  # Dictionary to store previous prices for comparison
        self.csv_filename = f"price_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Product ID', 'Product Name', 'Price', 'Currency', 'Change (%)', 'Significant Change'])
        
        logging.info(f"Price tracker initialized with base URL: {base_url}")
        logging.info(f"Data will be saved to: {self.csv_filename}")

    def get_all_products(self):
        """
        Fetch all products from the API.
        
        Returns:
            list: List of product data dictionaries or empty list if request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/products")
            response.raise_for_status()
            products = response.json()
            logging.info(f"Successfully fetched {len(products)} products")
            return products
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching products: {e}")
            return []
        except json.JSONDecodeError:
            logging.error("Error parsing product data")
            return []

    def get_product_details(self, product_id):
        """
        Fetch detailed information for a specific product.
        
        Args:
            product_id (str): The ID of the product to fetch
            
        Returns:
            dict: Product details or None if request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/products/{product_id}")
            response.raise_for_status()
            product_details = response.json()
            return product_details
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching product {product_id} details: {e}")
            return None
        except json.JSONDecodeError:
            logging.error(f"Error parsing product data for ID {product_id}")
            return None

    def get_product_price_from_page(self, product_id):
        """
        Scrape the product page to extract price information.
        
        Args:
            product_id (str): The ID of the product
            
        Returns:
            tuple: (product_name, price, currency) or (None, None, None) if scraping fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/product-page/{product_id}")
            response.raise_for_status()
            
            # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product name (adjust selectors based on actual HTML structure)
            product_name_elem = soup.find(string=lambda text: text and not text.strip().startswith('Product ID:'))
            product_name = product_name_elem.strip() if product_name_elem else "Unknown Product"
            
            # Extract price with regex (assuming the format "USD 628.61" as shown in the example)
            price_text = soup.find(string=re.compile(r'\*\*[A-Z]{3}\s\d+\.\d+\*\*'))
            
            if price_text:
                # Extract just the numbers and currency from the string
                price_match = re.search(r'\*\*([A-Z]{3})\s(\d+\.\d+)\*\*', price_text)
                if price_match:
                    currency = price_match.group(1)
                    price = float(price_match.group(2))
                    return product_name, price, currency
            
            # Alternative method if the above doesn't work
            # Try to find bold text (which might contain price)
            bold_text = soup.find('strong')
            if bold_text:
                price_text = bold_text.text
                price_match = re.search(r'([A-Z]{3})\s(\d+\.\d+)', price_text)
                if price_match:
                    currency = price_match.group(1)
                    price = float(price_match.group(2))
                    return product_name, price, currency
            
            logging.warning(f"Could not extract price information from product page {product_id}")
            return None, None, None
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching product page {product_id}: {e}")
            return None, None, None
        except Exception as e:
            logging.error(f"Error parsing product page for ID {product_id}: {e}")
            return None, None, None

    def calculate_price_change(self, product_id, current_price):
        """
        Calculate the percentage change in price compared to the last recorded price.
        
        Args:
            product_id (str): The ID of the product
            current_price (float): The current price of the product
            
        Returns:
            tuple: (percentage_change, is_significant_change)
        """
        if product_id not in self.product_history or self.product_history[product_id] == 0:
            return 0.0, False
        
        previous_price = self.product_history[product_id]
        price_change = ((current_price - previous_price) / previous_price) * 100
        
        is_significant = abs(price_change) >= self.significant_change_threshold
        
        return round(price_change, 2), is_significant

    def record_price(self, product_id, product_name, price, currency, price_change=0.0, is_significant=False):
        """
        Record the price data to the CSV file.
        
        Args:
            product_id (str): The ID of the product
            product_name (str): The name of the product
            price (float): The current price of the product
            currency (str): The currency of the price
            price_change (float): The percentage change in price
            is_significant (bool): Whether the price change is significant
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.csv_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, product_id, product_name, price, currency, price_change, is_significant])
        
        # Update the product history
        self.product_history[product_id] = price

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
            
            # Fetch all products
            products = self.get_all_products()
            
            for product in products:
                product_id = product.get('id')
                
                # Skip if product ID is missing
                if not product_id:
                    logging.warning("Found product without ID, skipping")
                    continue
                
                # First try to get price from product page (HTML scraping)
                product_name, price, currency = self.get_product_price_from_page(product_id)
                
                # If scraping failed, try to get product details from API
                if price is None:
                    product_details = self.get_product_details(product_id)
                    
                    # Skip if product details unavailable
                    if not product_details:
                        logging.warning(f"Could not fetch details for product ID: {product_id}")
                        continue
                    
                    # Extract price information from API response
                    try:
                        price = float(product_details.get('price', 0))
                        product_name = product_details.get('name', 'Unknown')
                        currency = product_details.get('currency', 'USD')
                    except (ValueError, TypeError) as e:
                        logging.error(f"Error processing price data for product {product_id}: {e}")
                        continue
                
                # Skip if price is still None after both attempts
                if price is None:
                    logging.warning(f"Could not determine price for product {product_id}, skipping")
                    continue
                
                # Calculate price change if we have history
                price_change, is_significant = self.calculate_price_change(product_id, price)
                
                # Skip recording if price hasn't changed and this isn't the first record
                if product_id in self.product_history and price == self.product_history[product_id]:
                    logging.info(f"No price change for product {product_id}, skipping record")
                    continue
                
                # Record the price data
                self.record_price(product_id, product_name, price, currency, price_change, is_significant)
                
                if is_significant:
                    logging.warning(f"Significant price change detected for {product_name}: {price_change}%")
                else:
                    logging.info(f"Recorded price for {product_name}: {price} {currency}")
            
            # Wait for the next tracking interval
            logging.info(f"Iteration {iterations} completed. Waiting {self.tracking_interval} seconds until next check.")
            time.sleep(self.tracking_interval)
        
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
                product_id = row['Product ID']
                products_tracked.add(product_id)
                
                if product_id not in price_changes:
                    price_changes[product_id] = []
                
                try:
                    change = float(row['Change (%)'])
                    price_changes[product_id].append(change)
                except (ValueError, TypeError):
                    continue
        
        # Print analysis results
        print("\n===== PRICE ANALYSIS SUMMARY =====")
        print(f"Total products tracked: {len(products_tracked)}")
        
        for product_id, changes in price_changes.items():
            if not changes:
                continue
                
            significant_changes = [c for c in changes if abs(c) >= self.significant_change_threshold]
            
            print(f"\nProduct ID: {product_id}")
            print(f"  Total price records: {len(changes)}")
            print(f"  Significant price changes: {len(significant_changes)}")
            
            if changes:
                print(f"  Max increase: {max(changes):.2f}%")
                print(f"  Max decrease: {min(changes):.2f}%")
                print(f"  Average change: {sum(changes)/len(changes):.2f}%")
        
        print("\nFull price history saved to:", self.csv_filename)

def main():
    # Configuration
    BASE_URL = "https://cyber.istenith.com"
    TRACKING_INTERVAL = 60  # Check prices every 60 seconds
    DURATION_MINUTES = 60   # Track for 60 minutes
    
    # Create and run the price tracker
    tracker = PriceTracker(
        base_url=BASE_URL,
        tracking_interval=TRACKING_INTERVAL,
        significant_change_threshold=5.0
    )
    
    try:
        tracker.track_prices(duration_minutes=DURATION_MINUTES)
        tracker.analyze_price_history()
    except KeyboardInterrupt:
        print("Price tracking stopped by user")
        tracker.analyze_price_history()
    except Exception as e:
        logging.critical(f"Fatal error in price tracker: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()