#!/usr/bin/env python3
import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_validation_log():
    """
    Checks for the validation log, calculates and displays the hit rate.
    Handles cases where the log file is missing or empty.
    """
    # Correct path to the validation log file
    csv_path = 'reports/validation_log_v2.csv'
    
    try:
        # Check if the file exists and is not empty
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            df = pd.read_csv(csv_path)
            
            # Basic validation of expected columns
            expected_cols = ['date', 'actual_jodi', 'predicted_top5']
            if not all(col in df.columns for col in expected_cols):
                logger.error(f"Validation log is malformed. Missing one of the expected columns: {expected_cols}")
                return pd.DataFrame(), 0

            # Calculate hit rate (example: based on top 5 hits)
            # The logic for hit rate might need to be more sophisticated depending on requirements
            total_predictions = len(df)
            total_hits = df['top5_hit'].sum() if 'top5_hit' in df.columns else 0
            hit_rate = (total_hits / total_predictions) * 100 if total_predictions > 0 else 0
            
            logger.info(f"✅ Validation data found: {total_hits} hits in {total_predictions} games.")
            logger.info(f"📊 HIT RATE (Top 5): {hit_rate:.2f}%")
            
            print("\n--- Latest Validation Results ---")
            print(df.tail())
            return df, hit_rate
        else:
            # Handle case where file is missing or empty
            raise FileNotFoundError

    except FileNotFoundError:
        logger.warning("No validation data available to calculate hit rate.")
        print(f"--> Could not find or read the validation log: {csv_path}")
        print("--> This file is generated automatically when the main analysis runs on a new day's data.")
        print("\nExpected format for the CSV file:")
        print("date,prediction_date,actual_jodi,predicted_top5,hit_rank,top1_hit,top3_hit,top5_hit,confidence,report_path")
        return pd.DataFrame(), 0
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame(), 0

if __name__ == "__main__":
    check_validation_log()
