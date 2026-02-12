import logging
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import random
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KalyanEngine:
    """
    Handles data loading, preprocessing, and dummy data generation for Kalyan Matka analysis.
    Ensures data consistency and provides historical data.
    """

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df = self._load_or_create_data()

    def _generate_dummy_data(self, start_date: datetime, num_days: int = 30) -> pd.DataFrame:
        """
        Generates dummy data for the specified number of days starting from start_date.
        Ensures 'jodi' is a string or None for Sundays, and generates placeholder sangams.
        """
        dates = [start_date - timedelta(days=i) for i in range(num_days -1 , -1, -1)] # Generate dates in ascending order
        
        data = []
        for d in dates:
            open_digit = None
            close_digit = None
            jodi = None
            open_sangam = None
            close_sangam = None

            # Exclude Sundays
            if d.weekday() != 6:  # Monday is 0, Sunday is 6
                # Generate random digits (0-9)
                open_digit = random.randint(0, 9)
                close_digit = random.randint(0, 9)
                jodi = f"{open_digit}{close_digit}"

                # Generate placeholder sangams (3 random digits including open/close)
                # This is a simplification and not actual Kalyan Panna logic
                open_sangam_val = [str(open_digit)]
                close_sangam_val = [str(close_digit)]
                for _ in range(2):
                    open_sangam_val.append(str(random.randint(0, 9)))
                    close_sangam_val.append(str(random.randint(0, 9)))
                random.shuffle(open_sangam_val)
                random.shuffle(close_sangam_val)
                open_sangam = "".join(open_sangam_val)
                close_sangam = "".join(close_sangam_val)
            
            data.append({
                "date": d.strftime("%Y-%m-%d"),
                "open": open_digit,
                "close": close_digit,
                "jodi": jodi,
                "open_sangam": open_sangam,
                "close_sangam": close_sangam
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure 'open' and 'close' are Int64 (to allow None, which becomes NaN then Int64 with pd.NA)
        df['open'] = df['open'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        df['close'] = df['close'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        
        # Handle 'jodi', 'open_sangam', 'close_sangam' as string
        df['jodi'] = df['jodi'].apply(lambda x: None if x is None else str(x))
        df['open_sangam'] = df['open_sangam'].apply(lambda x: None if x is None else str(x))
        df['close_sangam'] = df['close_sangam'].apply(lambda x: None if x is None else str(x))

        return df

    def _load_or_create_data(self) -> pd.DataFrame:
        """
        Loads data from the CSV path or generates dummy data if the file is not found,
        is empty, or has insufficient data.
        """
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            try:
                # Read 'jodi', 'open_sangam', 'close_sangam' as string type
                df = pd.read_csv(self.csv_path, dtype={'jodi': str, 'open_sangam': str, 'close_sangam': str})
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(by='date').reset_index(drop=True)

                if 'open' in df.columns:
                    df['open'] = pd.to_numeric(df['open'], errors='coerce').astype('Int64')
                if 'close' in df.columns:
                    df['close'] = pd.to_numeric(df['close'], errors='coerce').astype('Int64')
                
                # Check for required sangam columns, and if missing, generate placeholders
                if 'open_sangam' not in df.columns or 'close_sangam' not in df.columns:
                    logging.warning("Missing 'open_sangam' or 'close_sangam' in CSV. Generating placeholders.")
                    df['open_sangam'] = df['open'].apply(
                        lambda x: f"{x}{random.randint(0,9)}{random.randint(0,9)}" if pd.notna(x) else None
                    ).astype(str)
                    df['close_sangam'] = df['close'].apply(
                        lambda x: f"{random.randint(0,9)}{x}{random.randint(0,9)}" if pd.notna(x) else None
                    ).astype(str)

                # Filter out rows with NA date or if key columns are entirely missing
                df = df.dropna(subset=['date', 'jodi', 'open_sangam', 'close_sangam'])

                if not df.empty and len(df) >= 7: # Ensure at least 7 days of data
                    logging.info(f"Loaded {len(df)} records from {self.csv_path}")
                    return df
                else:
                    logging.warning(
                        f"Insufficient data in {self.csv_path}. Generating dummy data."
                    )
            except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
                logging.error(f"Error reading {self.csv_path}: {e}. Generating dummy data.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}. Generating dummy data.")
        else:
            logging.warning(f"CSV file not found or is empty at {self.csv_path}. Generating dummy data.")

        # If data loading fails or is insufficient, generate dummy data
        dummy_df = self._generate_dummy_data(datetime.now())
        dummy_df.to_csv(self.csv_path, index=False) # Save dummy data
        logging.info(f"Generated and saved dummy data to {self.csv_path}")
        return dummy_df

    def get_historical_data(self) -> pd.DataFrame:
        """
        Returns the processed historical data.
        """
        return self.df

    def get_all_jodis(self) -> List[str]:
        """
        Returns a list of all possible Kalyan jodis (00-99).
        """
        return [f"{i}{j}" for i in range(10) for j in range(10)]
