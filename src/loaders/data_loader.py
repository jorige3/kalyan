from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/kalyan.csv")


def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    df['date'] = pd.to_datetime(df['date'], format='mixed')
    return df
