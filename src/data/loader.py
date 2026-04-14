import pandas as pd
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataLoader:
    """Handles loading and preprocessing of Kalyan market data."""
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        
    def load_data(self) -> pd.DataFrame:
        """Loads data from CSV and ensures correct types."""
        if not self.csv_path.exists():
            logger.error(f"Data file not found at {self.csv_path}")
            raise FileNotFoundError(f"Data file not found at {self.csv_path}")
            
        try:
            df = pd.read_csv(self.csv_path, dtype={
                'jodi': str,
                'open_panel': str,
                'close_panel': str,
                'sangam': str
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Basic validation of required columns
            required_cols = ['date', 'open_panel', 'jodi', 'close_panel', 'sangam']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                logger.error(f"Missing columns in data: {missing}")
                raise ValueError(f"Missing columns: {missing}")
                
            # Derived columns for easier analysis
            df['jodi'] = df['jodi'].str.zfill(2)
            
            # Filter out non-numeric jodi values (like 'xx')
            numeric_mask = df['jodi'].str.isnumeric()
            if (~numeric_mask).any():
                invalid_count = (~numeric_mask).sum()
                logger.warning(f"Dropping {invalid_count} rows with non-numeric jodi: {df.loc[~numeric_mask, 'jodi'].unique()}")
                df = df[numeric_mask].copy()
                
            df['open_digit'] = df['jodi'].str[0].astype(int)
            df['close_digit'] = df['jodi'].str[1].astype(int)
            
            logger.info(f"Successfully loaded {len(df)} records from {self.csv_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
