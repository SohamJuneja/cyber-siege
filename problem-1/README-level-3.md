# Stealth E-commerce Price Tracker

This advanced application tracks price fluctuations across e-commerce platforms by bypassing CAPTCHA and anti-bot detection systems. It uses sophisticated techniques to mimic human behavior while collecting pricing data.

## Features

- **CAPTCHA Bypass**: Uses undetected Chrome driver and human-like browsing patterns to bypass anti-bot protections
- **Dynamic User Behavior**: Implements random delays, scrolling patterns, and user-agent rotation
- **Auto-Retry System**: Automatically retries when encountering CAPTCHA or extraction failures
- **Multi-Site Support**: Works with Walmart, Best Buy, and is extensible to other e-commerce sites
- **Price Change Analysis**: Detects and reports significant price fluctuations
- **Detailed Logging**: Maintains comprehensive logs of all activities and issues

## Requirements

- Python 3.7+
- Required Python packages:
  - selenium
  - undetected-chromedriver
  - fake-useragent
  - beautifulsoup4 (optional, for more complex extraction)

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install selenium undetected-chromedriver fake-useragent
   ```

3. Ensure you have Chrome browser installed on your system

4. Create a `config.json` file or use the default that will be generated on first run

## Configuration

The script uses a `config.json` file with the following structure:

```json
{
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
  "session_duration": 120
}
```

## How to Run

1. Basic usage:
   ```
   python stealth_price_tracker.py
   ```

2. With custom parameters:
   ```
   python stealth_price_tracker.py --config custom_config.json --duration 120 --interval-min 45 --interval-max 90 --threshold 3.5
   ```

## Command Line Arguments

- `--config`: Path to configuration file (default: config.json)
- `--duration`: Duration to track prices in minutes (default: 60)
- `--interval-min`: Minimum interval between checks in seconds (default: 30)
- `--interval-max`: Maximum interval between checks in seconds (default: 60)
- `--threshold`: Threshold for significant price changes in percentage (default: 5.0)

## Output

The script generates two files:

1. `price_history_YYYYMMDD_HHMMSS.csv` - Contains all price data with timestamps
2. `stealth_price_tracker.log` - Contains logs of the tracking process

## Anti-Detection Techniques

This script employs several techniques to avoid detection:

1. **Browser Fingerprint Randomization**:
   - Random window sizes
   - Rotating user agents
   - Disabled automation flags

2. **Human-like Behavior**:
   - Natural scrolling patterns
   - Variable timing between actions
   - Random mouse movements (simulated)
   - Session cookies to appear as returning