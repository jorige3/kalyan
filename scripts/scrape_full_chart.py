import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import os
import logging

URL = "https://dpboss.boston/panel-chart-record/kalyan.php?full_chart"
CSV_PATH = "data/kalyan.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    range_pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})to(\d{1,2}/\d{1,2}/\d{4})')

    data = []

    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        first_text = cells[0].get_text(strip=True)
        match = range_pattern.search(first_text)

        if not match:
            continue

        start_date = datetime.strptime(match.group(1), "%d/%m/%Y")
        current_date = start_date

        values = [c.get_text(strip=True) for c in cells[1:] if c.get_text(strip=True).isdigit()]

        # Process in chunks of 3 (Mon–Sat)
        for i in range(0, len(values), 3):
            chunk = values[i:i+3]
            if len(chunk) < 3:
                continue

            # Skip Sundays
            while current_date.weekday() == 6:
                current_date += timedelta(days=1)

            open_panel = chunk[0]
            jodi = chunk[1]
            close_panel = chunk[2]

            open_digit = open_panel[-1]
            close_digit = close_panel[-1]

            record = {
                "date": current_date.strftime("%Y-%m-%d"),
                "open_panel": open_panel,
                "jodi": jodi,
                "close_panel": close_panel,
                "sangam": f"{open_panel}-{close_panel}"
            }

            data.append(record)
            current_date += timedelta(days=1)

    print("Total rows parsed:", len(data))
    return data


def save_to_csv(data):
    if len(data) < 500:
        logger.error("Too few rows scraped. Aborting overwrite.")
        return

    df = pd.DataFrame(data)
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"])
    
    # Explicit column order
    df = df[["date", "open_panel", "jodi", "close_panel", "sangam"]]

    os.makedirs("data", exist_ok=True)
    df.to_csv(CSV_PATH, index=False)

    logger.info(f"Saved {len(df)} rows to {CSV_PATH}")


if __name__ == "__main__":
    logger.info("Starting full chart scrape...")
    full_data = scrape()
    save_to_csv(full_data)
