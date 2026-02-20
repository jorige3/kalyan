import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import re

# Create logs directory if it doesn't exist
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(level=logging.INFO, filename=os.path.join(LOG_DIR, 'scrape.log'), filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_historical():
    """
    Scrapes the Kalyan panel chart table and extracts date, open, close, jodi, and panel data.
    Parses cell content that contains combined data like: "19,990,559,579-82"
    """
    url = 'https://dpboss.boston/panel-chart-record/kalyan.php#bottom'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    table = soup.find('table', class_='table-bordered')
    if not table:
        logger.warning("Could not find table with class 'table-bordered'. Trying any table.")
        table = soup.find('table')
        if not table:
            logger.error("No table found on the page.")
            return []

    historical_data = []
    date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')

    rows = table.find_all('tr')
    logger.info(f"Found {len(rows)} rows in the table.")

    # Skip header row if present
    if len(rows) > 0 and rows[0].find('th'):
        rows = rows[1:]

    for row_idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue

        # Find base date (usually in first cell)
        base_date = None
        for cell in cells[:3]:  # Check first few cells for date
            cell_text = cell.get_text(strip=True)
            match = date_pattern.search(cell_text)
            if match:
                try:
                    base_date = datetime.strptime(match.group(1), '%d/%m/%Y')
                    logger.info(f"Row {row_idx}: Found base date {base_date.strftime('%Y-%m-%d')}")
                    break
                except ValueError as e:
                    logger.error(f"Error parsing date '{match.group(1)}': {e}")
                    continue
        
        if not base_date:
            logger.warning(f"Skipping row {row_idx} - no valid date found")
            continue

        # Process data cells (skip date cell, process subsequent cells)
        current_date = base_date
        day_offset = 0
        
        for i in range(len(cells)):
            cell = cells[i]
            cell_text = cell.get_text(strip=True)
            
            # Skip if empty or just contains date
            if not cell_text or date_pattern.search(cell_text):
                day_offset += 1
                continue
            
            # Parse the combined data format like "19,990,559,579-82"
            parsed_data = parse_combined_cell_data(cell_text)
            if parsed_data:
                current_date = base_date + timedelta(days=day_offset)
                
                # Skip Sundays
                while current_date.weekday() == 6:
                    current_date += timedelta(days=1)
                
                formatted_date = current_date.strftime('%Y-%m-%d')
                row_data = {
                    'date': formatted_date,
                    'open': parsed_data['open'],
                    'close': parsed_data['close'],
                    'jodi': parsed_data['jodi'],
                    'panel': parsed_data['panel']
                }
                historical_data.append(row_data)
                logger.info(f"Parsed: {formatted_date} - {row_data}")
                day_offset += 1

    logger.info(f"Scraped {len(historical_data)} historical records.")
    return historical_data

def parse_combined_cell_data(cell_text):
    """
    Parse cell text containing combined format like: "19,990,559,579-82"
    Returns dict with open, close, jodi, panel or None if unparseable
    """
    # Clean and normalize text
    cell_text = re.sub(r'[^\d,\s\-]', '', cell_text.strip())
    
    # Try comma-separated first
    parts = [p.strip() for p in cell_text.split(',') if p.strip()]
    if len(parts) >= 4:
        open_val = parts[0]
        close_val = parts[1] if len(parts[1]) == 3 else parts[0][-1]  # Sometimes open/close combined
        jodi_val = parts[2]
        panel_val = parts[3]
        
        return {
            'open': open_val[-1] if len(open_val) > 1 else open_val,  # Last digit as open
            'close': close_val[-1] if len(close_val) > 1 else close_val,
            'jodi': jodi_val,
            'panel': panel_val
        }
    
    # Try extracting all numbers and pattern matching
    numbers = re.findall(r'\d+', cell_text)
    if len(numbers) >= 4:
        # Common pattern: open_digit(1), open_panel(3), jodi(3), close_panel_part1(3)-close_panel_part2(2)
        if len(numbers[0]) == 1:
            open_digit = numbers[0]
            open_panel = numbers[1]
            jodi = numbers[2]
            panel = '-'.join(numbers[3:])
        else:
            # Fallback: first digit(s) as open, next as close, then jodi, rest as panel
            open_digit = numbers[0][-1]  # Last digit of first number
            close_digit = numbers[1][-1] if len(numbers) > 1 else '0'
            jodi = numbers[2] if len(numbers) > 2 else '00'
            panel = '-'.join(numbers[3:]) if len(numbers) > 3 else numbers[3]
        
        return {
            'open': open_digit,
            'close': close_digit,
            'jodi': jodi,
            'panel': panel
        }
    
    logger.warning(f"Could not parse cell data: '{cell_text}' (numbers: {re.findall(r'\\d+', cell_text)})")
    return None

def append_to_csv(new_data, csv_path='data/kalyan.csv'):
    """Appends new data to CSV while avoiding duplicates based on date."""
    if not new_data:
        logger.info("No new data to append.")
        return

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        try:
            df_existing = pd.read_csv(csv_path)
            existing_dates = set(df_existing['date'].astype(str))
            new_data_to_add = [row for row in new_data if row['date'] not in existing_dates]
            
            if not new_data_to_add:
                logger.info("All scraped data already exists in CSV.")
                return
            
            df_new = pd.DataFrame(new_data_to_add)
        except Exception as e:
            logger.warning(f"Could not read existing CSV: {e}. Creating new file.")
            df_new = pd.DataFrame(new_data)
    else:
        df_new = pd.DataFrame(new_data)
    
    df_new = df_new[['date', 'open', 'close', 'jodi', 'panel']]
    
    mode = 'a' if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0 else 'w'
    header = not (os.path.exists(csv_path) and os.path.getsize(csv_path) > 0)
    
    df_new.to_csv(csv_path, mode=mode, header=header, index=False)
    logger.info(f"Appended {len(df_new)} new rows to {csv_path}")

def overwrite_csv(data, csv_path='data/kalyan.csv'):
    """Overwrites the CSV with new data."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    if not data:
        logger.warning(f"No data provided. Creating empty CSV with header at {csv_path}")
        pd.DataFrame(columns=['date', 'open', 'close', 'jodi', 'panel']).to_csv(csv_path, index=False)
        return

    df = pd.DataFrame(data)
    df = df[['date', 'open', 'close', 'jodi', 'panel']]
    df.to_csv(csv_path, index=False)
    logger.info(f"Overwrote {csv_path} with {len(df)} rows.")

def main():
    """Main function to scrape and save data."""
    logger.info("Starting Kalyan panel chart scrape...")
    
    data = scrape_historical()
    
    if data:
        overwrite_csv(data)
        logger.info("Scraping completed successfully.")
    else:
        logger.error("No data scraped. Check logs for details.")

if __name__ == '__main__':
    main()
