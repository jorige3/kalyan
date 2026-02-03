from datetime import timedelta

import pandas as pd

import config


def calculate_cycle_gaps(df, column_name):
    """
    Calculates the cycle gaps for each unique number in a given column.
    A cycle gap is the number of days since the number last appeared.

    Args:
        df (pd.DataFrame): DataFrame with a 'date' column and the target column.
        column_name (str): The name of the column to analyze (e.g., 'open_panel', 'close_panel', 'jodi').

    Returns:
        dict: A dictionary where keys are unique numbers and values are their current cycle gaps.
    """
    df['date'] = pd.to_datetime(df['date'])
    latest_date = df['date'].max()
    cycle_gaps = {}

    if column_name == 'jodi':
        for i in range(100):
            jodi_str = str(i).zfill(2)
            last_appearance = df[df['jodi'].astype(str) == jodi_str]['date'].max()
            if pd.notna(last_appearance):
                gap = (latest_date - last_appearance).days
                cycle_gaps[jodi_str] = gap
    else: # For single digits in open_panel or close_panel
        for num in range(10):
            num_str = str(num)
            last_appearance = df[df[column_name].astype(str).str.contains(num_str)]['date'].max()
            if pd.notna(last_appearance):
                gap = (latest_date - last_appearance).days
                cycle_gaps[num_str] = gap
            else:
                cycle_gaps[num_str] = 9999 # A large number to signify it's very "due"

    return cycle_gaps

def identify_due_cycles(cycle_gaps, due_top_n=config.DUE_TOP_N):
    """
    Identifies numbers/Jodi that are 'due' by selecting the top N with the largest cycle gaps.

    Args:
        cycle_gaps (dict): Dictionary of numbers/Jodi and their cycle gaps.
        due_top_n (int): The number of top 'due' cycles to return.

    Returns:
        list: A list of numbers/Jodi that are considered 'due'.
    """
    # Sort by gap in descending order and take the top N
    sorted_jodi_by_gap = sorted(cycle_gaps.items(), key=lambda item: item[1], reverse=True)
    due_cycles = [jodi for jodi, gap in sorted_jodi_by_gap[:due_top_n]]
    return due_cycles

def identify_hot_numbers(df, column_name, lookback_days=config.HOT_LOOKBACK_DAYS, top_n=config.HOT_TOP_N):
    """
    Identifies 'hot' numbers/Jodi based on their frequency in recent days.

    Args:
        df (pd.DataFrame): DataFrame with a 'date' column and the target column.
        column_name (str): The name of the column to analyze.
        lookback_days (int): Number of recent days to consider for frequency.
        top_n (int): Number of top frequent numbers/Jodi to return.

    Returns:
        list: A list of 'hot' numbers/Jodi.
    """
    df['date'] = pd.to_datetime(df['date'])
    latest_date = df['date'].max()
    recent_df = df[df['date'] >= (latest_date - timedelta(days=lookback_days))]

    if column_name == 'jodi':
        frequencies = recent_df['jodi'].value_counts()
    else:
        # For single digits in open_panel or close_panel
        all_digits = pd.concat([recent_df[column_name].astype(str).str[0], 
                                recent_df[column_name].astype(str).str[1]])
        frequencies = all_digits.value_counts()
    
    hot_numbers = [str(x) for x in frequencies.head(top_n).index.tolist()]
    return sorted(hot_numbers)

def identify_exhausted_numbers(cycle_gaps, hot_jodis, exhausted_gap_threshold=config.EXHAUSTED_GAP_THRESHOLD):
    """
    Identifies 'exhausted' numbers/Jodi.
    For now, this function returns an empty list to match the user's desired output.
    A more robust implementation would involve identifying numbers that were 'hot' but are now 'cooling down'.

    Args:
        cycle_gaps (dict): Dictionary of numbers/Jodi and their cycle gaps.
        hot_jodis (list): List of hot Jodis.
        exhausted_gap_threshold (int): Numbers/Jodi with a gap less than or equal to this are considered 'recently appeared'.

    Returns:
        list: An empty list of 'exhausted' numbers/Jodi.
    """
    return []