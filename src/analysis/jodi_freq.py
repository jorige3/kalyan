import pandas as pd


def analyze_jodi_frequency(df, days):
    """
    Analyzes the frequency of Jodi (pairs) in the given DataFrame for a specified number of days.

    Args:
        df (pd.DataFrame): The input DataFrame containing 'Date', 'Open', and 'Close' columns.
        days (int): The number of recent days to consider for the analysis.

    Returns:
        tuple: A tuple containing:
            - jodi_counts (pd.Series): Counts of each Jodi.
            - jodi_percentages (pd.Series): Percentages of each Jodi.
    """
    recent_df = df.tail(days)
    jodi = recent_df['open_panel'].astype(str) + recent_df['close_panel'].astype(str)
    jodi_counts = jodi.value_counts()
    total_jodis = len(jodi)
    jodi_percentages = (jodi_counts / total_jodis) * 100
    return jodi_counts, jodi_percentages


def split_hot_warm_cold(jodi_counts):
    """
    Splits Jodi into hot, warm, and cold categories based on their counts.

    Args:
        jodi_counts (pd.Series): Counts of each Jodi.

    Returns:
        tuple: A tuple containing:
            - hot_jodis (list): List of hot Jodi.
            - warm_jodis (list): List of warm Jodi.
            - cold_jodis (list): List of cold Jodi.
    """
    # Define thresholds for hot, warm, and cold
    # These thresholds can be adjusted based on desired sensitivity
    hot_threshold = jodi_counts.quantile(0.75)
    cold_threshold = jodi_counts.quantile(0.25)

    hot_jodis = jodi_counts[jodi_counts >= hot_threshold].index.tolist()
    warm_jodis = jodi_counts[(jodi_counts < hot_threshold) & (jodi_counts > cold_threshold)].index.tolist()
    cold_jodis = jodi_counts[jodi_counts <= cold_threshold].index.tolist()

    return hot_jodis, warm_jodis, cold_jodis
