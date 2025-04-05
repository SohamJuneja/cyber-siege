# E-Commerce Price Tracker

A robust Python script that extracts product names and prices from various e-commerce websites. This tool supports both static HTML pages and dynamically rendered JavaScript content.

## Features

- Extracts product names and prices from multiple e-commerce platforms
- Supports both static and JavaScript-rendered pages
- Handles varying HTML structures with site-specific and generic extractors
- Standardizes price formats across different currencies and notations
- Provides detailed logging for troubleshooting
- Falls back gracefully when specific extractors fail

## Supported Sites

- Books To Scrape (books.toscrape.com)
- Meesho (meesho.com)
- Amazon (amazon.in, amazon.com, etc.)
- Flipkart (flipkart.com)
- Generic support for other e-commerce sites

## Requirements

- Python 3.7+
- Chrome/Chromium browser

## Dependencies

```
requests>=2.28.1
beautifulsoup4>=4.11.1
selenium>=4.1.0
webdriver-manager>=3.8.3
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cyber-siege.git
   cd cyber-siege/problem-1
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command Line

Run the script with a URL:
```
python level-1.py --url "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
```

Or run it and input the URL when prompted:
```
python level-1.py
```

To run the browser in visible mode (not headless):
```
python level-1.py --url "https://www.amazon.in/product-page" --no-headless
```

### As a Module

You can also import and use the `PriceTracker` class in your own scripts:

```python
from level_1 import PriceTracker

tracker = PriceTracker()
result = tracker.get_price("https://www.example.com/product")
print(result)
tracker.close()  # Important to close the browser when done
```

## Output Format

The script returns a dictionary with the following structure:

```python
{
    'success': True,  # or False if extraction failed
    'product_name': 'Product Name',
    'price': 1999.99,  # Numeric price
    'price_text': '₹1,999.99',  # Original price text
    'currency': 'INR',  # Currency code
    'url': 'https://example.com/product'
}
```

If extraction fails, it returns:
```python
{
    'success': False,
    'error': 'Error message',
    'url': 'https://example.com/product'
}
```

## Error Handling

The script handles the following errors:
- Network connection issues
- Page loading timeouts
- Missing HTML elements
- Browser automation failures
- Various price format inconsistencies

## Assumptions

1. The user has Chrome/Chromium installed on their system
2. The product pages follow common e-commerce layouts
3. Internet connectivity is available
4. Prices are displayed in a recognizable format
5. For JavaScript-heavy sites, Selenium will be used automatically

## License

MIT License