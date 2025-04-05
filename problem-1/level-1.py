import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_flipkart_products(url):
    logging.info(f"Fetching product info from Flipkart collection page")

    # Initialize WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove if you want to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(20)  # Wait for page to fully load

        # Scroll to load more products (optional: repeat for more)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20)

        # Find product containers
        products = driver.find_elements(By.CLASS_NAME, '_1AtVbE')

        found_any = False
        for product in products:
            try:
                title = product.find_element(By.CLASS_NAME, '_4rR01T').text
                price = product.find_element(By.CLASS_NAME, '_30jeq3').text
                print(f"{title} - {price}")
                found_any = True
            except:
                continue

        if not found_any:
            logging.error("No product info could be extracted. Try checking class names or increasing wait time.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    url = input("Enter Flipkart product collection URL: ").strip()
    get_flipkart_products(url)
