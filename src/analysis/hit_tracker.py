import json
import logging
import os
from datetime import datetime, timedelta

import pandas as pd

LOG_FILE = "reports/hit_log.csv"
REPORTS_DIR = "reports"

def track_hit_rate(df: pd.DataFrame, current_analysis_date: datetime, market_name: str = "Kalyan"):
    """
    Tracks the hit rate of predictions made on the previous day by comparing them
    with the actual results of the current day. The results are logged to a CSV file.

    Args:
        df (pd.DataFrame): The historical data DataFrame.
        current_analysis_date (datetime): The date for which the current analysis is being run.
                                           This is the date for which we seek the actual result.
        market_name (str): The name of the market (e.g., "Kalyan").
    """
    logging.info(f"Attempting to track hit rate for predictions relative to {current_analysis_date.date()}")

    # Ensure 'date' column is in datetime format for proper comparison
    df['date'] = pd.to_datetime(df['date'])

    # Determine yesterday's date (when predictions were made)
    yesterday_date = current_analysis_date - timedelta(days=1)

    # 1. Get yesterday's predictions from the snapshot JSON
    yesterday_predictions_file = os.path.join(REPORTS_DIR, f"kalyan_analysis_{yesterday_date.strftime('%Y-%m-%d')}.json")
    
    predicted_jodis = []
    if os.path.exists(yesterday_predictions_file):
        try:
            with open(yesterday_predictions_file, 'r') as f:
                snapshot_data = json.load(f)
                predictions_raw = snapshot_data.get("ranked_picks", [])
                predicted_jodis = [p["value"] for p in predictions_raw]
            logging.info(f"Loaded {len(predicted_jodis)} predictions from {yesterday_predictions_file}")
        except Exception as e:
            logging.error(f"Error loading predictions from {yesterday_predictions_file}: {e}")
    else:
        logging.warning(f"No prediction snapshot found for {yesterday_date.date()}. Skipping hit rate tracking for this date.")
        return # Cannot track if no predictions were made

    if not predicted_jodis:
        logging.warning(f"No predictions found in snapshot for {yesterday_date.date()}. Skipping hit rate tracking.")
        return

    # 2. Get today's actual result from the historical data
    actual_result_row = df[df['date'] == current_analysis_date]

    actual_jodi = None
    hit = False

    if not actual_result_row.empty:
        actual_jodi = str(actual_result_row.iloc[0]['jodi'])
        if actual_jodi in predicted_jodis:
            hit = True
            logging.info(f"🎉 HIT! Predicted Jodi '{actual_jodi}' from {yesterday_date.date()} was a hit on {current_analysis_date.date()}!")
        else:
            logging.info(f"⛔ NO HIT. Actual Jodi '{actual_jodi}' on {current_analysis_date.date()} not in predictions from {yesterday_date.date()}.")
    else:
        logging.warning(f"Actual result for {current_analysis_date.date()} not yet available in data. Cannot track hit rate.")
        return # Cannot track if no actual result is available

    # Log to CSV
    log_data = {
        "analysis_date": yesterday_date.strftime("%Y-%m-%d"), # Date predictions were made
        "result_date": current_analysis_date.strftime("%Y-%m-%d"), # Date actual result was checked
        "market": market_name,
        "predictions": ";".join(predicted_jodis), # Store predictions as a semicolon-separated string
        "actual_jodi": actual_jodi if actual_jodi else "N/A",
        "hit": hit,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    log_df = pd.DataFrame([log_data])
    
    # Ensure reports directory exists for hit_log.csv
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        log_df.to_csv(LOG_FILE, index=False)
    else:
        log_df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    
    logging.info(f"Hit rate tracking data logged to {LOG_FILE}")

