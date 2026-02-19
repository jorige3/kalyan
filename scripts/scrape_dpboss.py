import logging
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_kalyan_latest():
    url = "https://dpboss.boston/panel-chart-record/kalyan.php#bottom"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Select all table rows
    rows = soup.select('table tr')
    
    new_data = []
    # Process rows in reverse order to ensure we get the latest valid data
    for row in reversed(rows):
        cols = [td.text.strip() for td in row.find_all('td')]
        
        # Ensure we have at least 5 columns (date, open, close, jodi, panel)
        if len(cols) >= 5:
            date_str = cols[0]
            
            # Try to parse date in DD-MM-YYYY format, coercing errors to NaT
            try:
                # Some date strings might contain ranges like "26/01/2026to31/01/2026",
                # so we need to extract only the first date part if a range is present.
                if 'to' in date_str:
                    date_str = date_str.split('to')[0].strip()
                
                parsed_date = pd.to_datetime(date_str, format='%d-%m-%Y', errors='raise')
                
                # Format to YYYY-MM-DD for consistency
                formatted_date = parsed_date.strftime('%Y-%m-%d')
                
                # Replace original date string with formatted date
                cols[0] = formatted_date
                new_data.append(cols[:5])
            except ValueError:
                # Log invalid date format but continue
                logger.debug(f"Skipping row due to invalid date format: {date_str}")
                continue
    
    logger.info(f"Found {len(new_data)} potential new records from web scraping.")
    return new_data

def update_csv(new_rows):
    csv_path = 'data/kalyan.csv'
    
    # Check if the CSV exists and read it, otherwise create an empty DataFrame
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path, parse_dates=['date'])
        last_date_existing = df_existing['date'].max()
    else:
        df_existing = pd.DataFrame(columns=['date', 'open', 'close', 'jodi', 'panel'])
        last_date_existing = pd.to_datetime('1900-01-01') # A very old date if no file exists

    df_new = pd.DataFrame(new_rows, columns=['date', 'open', 'close', 'jodi', 'panel'])
    df_new['date'] = pd.to_datetime(df_new['date'])

    # Filter out records that are older than or equal to the last existing date
    df_new_filtered = df_new[df_new['date'] > last_date_existing]
    
    if df_new_filtered.empty:
        logger.info("No genuinely new records to add to kalyan.csv.")
        return
        
    df_combined = pd.concat([df_existing, df_new_filtered])
    
    # Ensure no duplicates and sort by date
    df_combined = df_combined.drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
    
    df_combined.to_csv(csv_path, index=False)
    logger.info(f"Updated {csv_path} with {len(df_new_filtered)} new rows.")

if __name__ == "__main__":
    new_data = scrape_kalyan_latest()
    update_csv(new_data)
