import pandas as pd
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def compute_jodi_matrix(df, last_n_days=60):
    """
    Builds a 00-99 probability matrix based on digit distributions and panel conditionals.
    
    score = 0.6 * base_probability + 0.4 * conditional_probability
    
    base_probability: P(open_digit) * P(close_digit)
    conditional_probability: P(open_digit | prev_open_panel_last) * P(close_digit | prev_close_panel_last)
    """
    if df.empty or len(df) < 2:
        return []

    # Sort by date and ensure data types
    df = df.sort_values('date').copy()
    df["jodi"] = df["jodi"].astype(str).str.zfill(2)
    
    # Extract digits
    df["open_digit"] = df["jodi"].str[0].astype(int)
    df["close_digit"] = df["jodi"].str[1].astype(int)
    
    # Last digits of panels
    df["open_panel_last"] = df["open_panel"].astype(str).str[-1].fillna('0').replace('', '0').astype(int)
    df["close_panel_last"] = df["close_panel"].astype(str).str[-1].fillna('0').replace('', '0').astype(int)
    
    # For conditional, we use previous day's panel last digit as the predictor
    df["prev_open_panel_last"] = df["open_panel_last"].shift(1)
    df["prev_close_panel_last"] = df["close_panel_last"].shift(1)
    
    # Latest day in the training set
    latest_date = df['date'].max()
    
    # Filter for last N days for base and conditional calculation (no leakage as we only use df)
    # Note: df passed here should already be filtered for backtesting
    analysis_start_date = latest_date - pd.Timedelta(days=last_n_days)
    analysis_df = df[df['date'] > analysis_start_date].dropna(subset=["prev_open_panel_last", "prev_close_panel_last"])
    
    if analysis_df.empty:
        return []

    # 1. Base Probabilities P(A) and P(B)
    open_freq = analysis_df["open_digit"].value_counts(normalize=True).reindex(range(10), fill_value=0)
    close_freq = analysis_df["close_digit"].value_counts(normalize=True).reindex(range(10), fill_value=0)
    
    # 2. Conditional Probabilities P(digit_t | prev_panel_last_{t-1})
    # Using crosstab to get P(digit | prev_panel)
    cond_open = pd.crosstab(analysis_df["prev_open_panel_last"], analysis_df["open_digit"], normalize='index')
    cond_close = pd.crosstab(analysis_df["prev_close_panel_last"], analysis_df["close_digit"], normalize='index')
    
    # Reindex to ensure all digits 0-9 are present for both index and columns
    cond_open = cond_open.reindex(index=range(10), columns=range(10), fill_value=0)
    cond_close = cond_close.reindex(index=range(10), columns=range(10), fill_value=0)
    
    # Last Known Panel Last Digits (the "conditions" for the next prediction)
    # This comes from the absolute latest row in our input dataframe
    latest_open_panel_last = int(df.iloc[-1]["open_panel_last"])
    latest_close_panel_last = int(df.iloc[-1]["close_panel_last"])
    
    matrix_scores = {}
    for i in range(10):
        for j in range(10):
            jodi = f"{i}{j}"
            
            # Base Probability
            base_prob = open_freq[i] * close_freq[j]
            
            # Conditional Probability given latest known panels
            p_a_given_x = cond_open.loc[latest_open_panel_last, i]
            p_b_given_y = cond_close.loc[latest_close_panel_last, j]
            cond_prob = p_a_given_x * p_b_given_y
            
            # Final Score combine
            score = (0.6 * base_prob) + (0.4 * cond_prob)
            matrix_scores[jodi] = score
            
    ranked = sorted(matrix_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked
