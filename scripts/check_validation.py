import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_validation_log():
    csv_path = 'reports/validation_log_v2.csv'
    
    try:
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            df = pd.read_csv(csv_path)
            hit_rate = len(df) / 101 * 100
            logger.info(f"✅ Validation data found: {len(df)}/101 successful predictions")
            logger.info(f"📊 HIT RATE: {hit_rate:.1f}%")
            print(df.tail())
            return df, hit_rate
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        logger.warning("No validation data available. Hit rate = 0%")
        print(f"{csv_path} missing or empty")
        print("Expected format:")
        print("date,prediction_date,actual_jodi,predicted_top5,hit_rank,top1_hit,top3_hit,top5_hit,confidence,report_path")
        return pd.DataFrame(), 0

if __name__ == "__main__":
    df, hit_rate = check_validation_log()
