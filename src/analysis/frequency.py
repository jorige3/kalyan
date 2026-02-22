import pandas as pd


def digit_frequency(df, column):
    """
    Returns frequency count of digits 0–9
    column: 'open' or 'close'
    """
    counts = df[column].value_counts().sort_index()
    result = pd.Series(0, index=range(10))
    result.update(counts)
    return result
