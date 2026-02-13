import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
    """
    Handles loading data from a CSV file or generating dummy data if the file
    is not found, empty, or contains insufficient data.
    """

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def get_data(self) -> pd.DataFrame:
        """
        Loads data from the CSV path or generates dummy data.
        """
        return self._load_or_create_data()

    def _generate_dummy_data(self, start_date: datetime, num_days: int = 30) -> pd.DataFrame:
        """
        Generates dummy data for the specified number of days starting from start_date.
        """
        dates = [start_date - timedelta(days=i) for i in range(num_days - 1, -1, -1)]
        data = []
        for d in dates:
            open_digit, close_digit, jodi, open_sangam, close_sangam = None, None, None, None, None
            if d.weekday() != 6:  # Exclude Sundays
                open_digit = random.randint(0, 9)
                close_digit = random.randint(0, 9)
                jodi = f"{open_digit}{close_digit}"
                open_sangam_val = [str(open_digit)] + [str(random.randint(0, 9)) for _ in range(2)]
                close_sangam_val = [str(close_digit)] + [str(random.randint(0, 9)) for _ in range(2)]
                random.shuffle(open_sangam_val)
                random.shuffle(close_sangam_val)
                open_sangam = "".join(open_sangam_val)
                close_sangam = "".join(close_sangam_val)
            
            data.append({
                "date": d.strftime("%Y-%m-%d"), "open": open_digit, "close": close_digit,
                "jodi": jodi, "open_sangam": open_sangam, "close_sangam": close_sangam
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['open'] = df['open'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        df['close'] = df['close'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        df['jodi'] = df['jodi'].apply(lambda x: None if x is None else str(x))
        df['open_sangam'] = df['open_sangam'].apply(lambda x: None if x is None else str(x))
        df['close_sangam'] = df['close_sangam'].apply(lambda x: None if x is None else str(x))
        return df

    def _load_or_create_data(self) -> pd.DataFrame:
        """
        Loads data from CSV or generates dummy data if loading fails.
        """
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            try:
                df = pd.read_csv(self.csv_path, dtype={'jodi': str, 'open_sangam': str, 'close_sangam': str})
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(by='date').reset_index(drop=True)

                if 'open' in df.columns:
                    df['open'] = pd.to_numeric(df['open'], errors='coerce').astype('Int64')
                if 'close' in df.columns:
                    df['close'] = pd.to_numeric(df['close'], errors='coerce').astype('Int64')
                
                if 'open_sangam' not in df.columns or 'close_sangam' not in df.columns:
                    logging.warning("Missing sangam columns in CSV. Generating placeholders.")
                    df['open_sangam'] = df['open'].apply(lambda x: f"{x}{random.randint(0,9)}{random.randint(0,9)}" if pd.notna(x) else None).astype(str)
                    df['close_sangam'] = df['close'].apply(lambda x: f"{random.randint(0,9)}{x}{random.randint(0,9)}" if pd.notna(x) else None).astype(str)
                
                df = df.dropna(subset=['date', 'jodi', 'open_sangam', 'close_sangam'])

                if not df.empty and len(df) >= 7:
                    logging.info(f"Loaded {len(df)} records from {self.csv_path}")
                    return df
                else:
                    logging.warning(f"Insufficient data in {self.csv_path}. Generating dummy data.")
            except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
                logging.error(f"Error reading {self.csv_path}: {e}. Generating dummy data.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}. Generating dummy data.")
        else:
            logging.warning(f"CSV file not found or is empty at {self.csv_path}. Generating dummy data.")

        dummy_df = self._generate_dummy_data(datetime.now())
        dummy_df.to_csv(self.csv_path, index=False)
        logging.info(f"Generated and saved dummy data to {self.csv_path}")
        return dummy_df
