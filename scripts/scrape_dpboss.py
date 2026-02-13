import logging
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_kalyan_latest():
    url = "https://dpboss.boston/panel-chart-record/kalyan.php#bottom"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    rows = soup.select('table tr')[-5:]  # Get more rows for safety
    
    new_data = []
    for row in rows:
        cols = [td.text.strip() for td in row.find_all('td')]
        if len(cols) >= 5:
            date_str = cols[0]
            # VALIDATE DATE FORMAT (YYYY-MM-DD only)
            try:
                test_date = pd.to_datetime(date_str)
                if test_date.year >= 2025:  # Only future dates
                    new_data.append(cols[:5])
            except Exception:
                continue  # Skip junk like "26/01/2026to31/01/2026"
    
    logger.info(f"Found {len(new_data)} valid new records")
    return new_data

def update_csv(new_rows):
    csv_path = 'data/kalyan.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=['date','open','close','jodi','panel'])
    
    # Append only new dates
    new_df = pd.DataFrame(new_rows, columns=['date','open','close','jodi','panel'])
    df = pd.concat([df, new_df]).drop_duplicates('date').sort_values('date')
    df.to_csv(csv_path, index=False)
    logger.info(f"Updated {csv_path} with {len(new_rows)} new rows")

if __name__ == "__main__":
    new_data = scrape_kalyan_latest()
    update_csv(new_data)
