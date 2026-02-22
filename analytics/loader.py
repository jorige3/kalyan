import pandas as pd

CSV_PATH = "data/kalyan.csv"

def load_data(with_digits=True):
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    df = df.sort_values("date")

    if with_digits:
        df["open"] = df["open_panel"].astype(str).str[-1].astype(int)
        df["close"] = df["close_panel"].astype(str).str[-1].astype(int)

    return df

