import glob
import os
import re
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

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
        latest_results = "No recent data"
        try:
            with open('data/kalyan.csv', 'r') as f:
                lines = f.readlines()
                latest_results = ''.join(lines[-3:]).strip()
        except FileNotFoundError:
            pass # It's okay if data file doesn't exist yet


        # 4. Build report
        report = f"""
🚀 KALYAN AI PREDICTIONS | {datetime.now().strftime('%d-%b-%Y %H:%M')}

📊 HIT RATE: {hit_rate:.1f}%
🎯 TOP PREDICTIONS: {', '.join(predictions[:4])}

📈 LATEST RESULTS:
{latest_results}

🔗 DASHBOARD: github.com/jorige3/kalyan
💻 Ollama: qwen2.5-coder:1.5b running
        """

        # 5. Send via Telegram (.env secure)
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ .env missing! Create .env with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
            return

        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {'chat_id': chat_id, 'text': report, 'parse_mode': 'HTML'}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Daily Kalyan report sent to Telegram!")
        else:
            print(f"❌ Telegram failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Report failed: {e}")

if __name__ == "__main__":
    send_daily_report()
