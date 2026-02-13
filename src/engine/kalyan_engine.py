import logging
from typing import List

import pandas as pd

from src.loaders.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KalyanEngine:
    """
    Handles preprocessing and provides historical data for Kalyan Matka analysis.
    Data loading is delegated to the DataLoader class.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        loader = DataLoader(csv_path=self.csv_path)
        self.df = loader.get_data()

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

