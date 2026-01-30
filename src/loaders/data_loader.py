import pandas as pd
from pathlib import Path


DATA_FILE = Path("data/kalyan.csv")


def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    return df
