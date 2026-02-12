import logging
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import random

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
        Ensures 'jodi' is a string or None for Sundays.
        """
        dates = [start_date - timedelta(days=i) for i in range(num_days -1 , -1, -1)] # Generate dates in ascending order
        
        data = []
        for d in dates:
            open_digit = None
            close_digit = None
            jodi = None

            # Exclude Sundays
            if d.weekday() != 6:  # Monday is 0, Sunday is 6
                # Generate random digits (0-9)
                open_digit = random.randint(0, 9)
                close_digit = random.randint(0, 9)
                jodi = f"{open_digit}{close_digit}"
            
            data.append({
                "date": d.strftime("%Y-%m-%d"),
                "open": open_digit,
                "close": close_digit,
                "jodi": jodi
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure 'open' and 'close' are Int64 (to allow None, which becomes NaN then Int64 with pd.NA)
        # Convert explicit None to pd.NA for proper handling in pandas integer columns
        df['open'] = df['open'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        df['close'] = df['close'].apply(lambda x: pd.NA if x is None else x).astype('Int64')
        
        # Handle 'jodi' as string, converting None to actual None object (which pandas stores as NaN for object dtype)
        df['jodi'] = df['jodi'].apply(lambda x: None if x is None else str(x))

        return df

    def _load_or_create_data(self) -> pd.DataFrame:
        """
        Loads data from the CSV path or generates dummy data if the file is not found,
        is empty, or has insufficient data.
        """
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            try:
                # Read 'jodi' as string to prevent pandas from inferring numeric type
                df = pd.read_csv(self.csv_path, dtype={'jodi': str})
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(by='date').reset_index(drop=True)

                if 'open' in df.columns:
                    df['open'] = pd.to_numeric(df['open'], errors='coerce').astype('Int64')
                if 'close' in df.columns:
                    df['close'] = pd.to_numeric(df['close'], errors='coerce').astype('Int64')
                
                # Filter out rows with NA date or if 'jodi' is entirely missing
                df = df.dropna(subset=['date'])
                if 'jodi' in df.columns:
                    df = df.dropna(subset=['jodi'])

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