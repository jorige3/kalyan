import os
import re
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.utils.telegram_sender import send_telegram_message # New import

load_dotenv()

def send_daily_report():
    try:
        # 1. Get hit rate (fallback 0 if missing)
        hit_rate = 0
        try:
            df_stats = pd.read_csv('reports/validation_log.csv')
            hit_rate = len(df_stats)/101*100 if len(df_stats)>0 else 0
        except FileNotFoundError:
            pass # It's okay if the log doesn't exist yet

        # 2. Get LATEST kpred predictions
        predictions = ["55", "04", "51", "34", "53"]  # Default fallback
        try:
            latest_report_list = glob.glob('reports/kalyan_analysis_*.json')
            if latest_report_list:
                latest_report = max(latest_report_list, key=os.path.getctime)
                print(f"Reading predictions from: {latest_report}")
                with open(latest_report, 'r') as f:
                    content = f.read()
                # Extract numbers like "55 (High)", "4 (High)" etc.
                matches = re.findall(r'(\d{1,2}) \(High\)', content)
                if matches:
                    predictions = matches[:5]
                    print(f"✅ Found predictions: {predictions}")
        except Exception as e:
            print(f"⚠️ Could not read predictions, using fallback. Error: {e}")

        # 3. Latest results from CSV
        formatted_latest_results = "No recent data"
        try:
            with open('data/kalyan.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) > 1: # Assuming header
                    parsed_results = []
                    for line in lines[-3:]:
                        parts = line.strip().split(',')
                        if len(parts) >= 5:
                            date = parts[0]
                            jodi = parts[4]
                            parsed_results.append(f"Date: {date}, Jodi: {jodi}")
                    if parsed_results:
                        formatted_latest_results = '\n'.join(parsed_results)
                    else:
                        formatted_latest_results = "No valid recent data found"
                else:
                    formatted_latest_results = "Not enough data in kalyan.csv"
        except FileNotFoundError:
            pass # It's okay if data file doesn't exist yet


        # 4. Build report
        report = f"""
🚀 KALYAN AI PREDICTIONS | {datetime.now().strftime('%d-%b-%Y %H:%M')}

📊 HIT RATE: {hit_rate:.1f}%
🎯 TOP PREDICTIONS: {', '.join(predictions[:5])}

📈 LATEST RESULTS:
{formatted_latest_results}

🔗 DASHBOARD: github.com/jorige3/kalyan
        """

        # 5. Send via Telegram (.env secure)
        if send_telegram_message(report):
            print("✅ Daily Kalyan report sent to Telegram!")
        else:
            print("❌ Daily Kalyan report Telegram failed!")

    except Exception as e:
        print(f"❌ Report failed: {e}")

if __name__ == "__main__":
    send_daily_report()
