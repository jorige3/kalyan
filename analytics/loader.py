import pandas as pd


def load_data(path="data/kalyan.csv", with_digits=True):
    print("LOADING FILE:", path)

    df = pd.read_csv(path, parse_dates=["date"])
    print("COLUMNS BEFORE:", df.columns.tolist())

    df = df.sort_values("date")

    if with_digits:
        df["open"] = df["open_panel"].astype(str).str[-1].astype(int)
        df["close"] = df["close_panel"].astype(str).str[-1].astype(int)

    print("COLUMNS AFTER:", df.columns.tolist())

    return df
