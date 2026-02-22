import pandas as pd


def normalize(series):
    # Prevent division by zero
    if series.max() == series.min():
        return pd.Series(0.0, index=series.index)

    return (series - series.min()) / (series.max() - series.min())


def weighted_score(freq_dict, gap_dict, w_freq=0.4, w_gap=0.6):
    freq = pd.Series(freq_dict)
    gap = pd.Series(gap_dict)

    freq_norm = normalize(freq)
    gap_norm = normalize(gap)

    score = (freq_norm * w_freq) + (gap_norm * w_gap)

    return score.sort_values(ascending=False)
