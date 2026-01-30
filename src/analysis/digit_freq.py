from collections import Counter
import pandas as pd


def analyze_jodi_frequency(df: pd.DataFrame, days: int) -> Counter:
    """
    Analyze jodi frequency for last N days.
    """
    recent_df = df.tail(days)
    jodis = recent_df["jodi"].astype(str).str.zfill(2)
    return Counter(jodis)


def split_hot_warm_cold(counter: Counter):
    """
    Split jodis into hot / warm / cold buckets.
    """
    if not counter:
        return [], [], []

    values = list(counter.values())
    max_v = max(values)
    min_v = min(values)

    hot = [j for j, c in counter.items() if c >= max_v * 0.7]
    cold = [j for j, c in counter.items() if c <= min_v * 1.3]
    warm = [j for j in counter if j not in hot and j not in cold]

    return sorted(hot), sorted(warm), sorted(cold)
