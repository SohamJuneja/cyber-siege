# E-commerce Price Tracker

This application tracks and analyzes price fluctuations across multiple products on an e-commerce platform. It detects significant price changes (>5% movement) and generates a detailed price history report in CSV format.

## Features

- Tracks multiple products simultaneously over a defined period
- Records price history with timestamps in CSV format
- Detects significant price changes (>5% movement)
- Handles edge cases such as duplicate entries, missing products, and price inconsistencies
- Provides analysis of price fluctuations

## Requirements

- Python 3.6+
- Required Python packages:
  - requests
  - csv (standard library)
  - time (standard library)
  - datetime (standard library)
  - os (standard library)
  - logging (standard library)

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install requests
   ```

## How to Run

1. Run the script:
   ```
   python price_tracker.py
   ```

2. The script will:
   - Start tracking product prices from the API
   - Record price data to a CSV file
   - Log activities to a log file
   - Display a summary analysis after completion

## Configuration

You can modify the following parameters in the `main()` function:

- `BASE_URL`: The API endpoint (default: "https://cyber.istenith.com")
- `TRACKING_INTERVAL`: Time between price checks in seconds (default: 60 seconds)
- `DURATION_MINUTES`: How long to track prices (default: 60 minutes)
- `significant_change_threshold`: Percentage threshold for significant price changes (default: 5.0%)

## Output

The script generates two files:

1. `price_history_YYYYMMDD_HHMMSS.csv` - Contains all price data with timestamps
2. `price_tracker.log` - Contains logs of the tracking process

## Assumptions

- The API endpoint returns JSON data
- Product data includes 'id', 'name', 'price', and 'currency' fields
- Price changes are considered significant if they vary by 5% or more
- The API has endpoints for:
  - Listing all products: `/products`
  - Getting product details: `/products/{product_id}`
- All prices are numeric values that can be converted to float
- The API may occasionally have missing products or inconsistent data