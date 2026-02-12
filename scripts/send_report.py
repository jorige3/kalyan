import requests
import pandas as pd
import glob
from datetime import datetime

def send_daily_report():
    try:
        # Read latest data
        latest_report = glob.glob('reports/kalyan_analysis_*.json')[0]
        df_stats = pd.read_csv('reports/validation_log.csv')
        hit_rate = len(df_stats)/101*100 if len(df_stats)>0 else 0
        
        # Latest predictions (update these from your kpred output)
        predictions = ["51", "04", "55", "34", "17"]
        
        # Latest results
        with open('data/kalyan.csv', 'r') as f:
            lines = f.readlines()
            latest_results = ''.join(lines[-3:])

        # Build beautiful report
        report = f"""
🚀 KALYAN AI PREDICTIONS | {datetime.now().strftime('%d-%b-%Y %H:%M')}

📊 HIT RATE: {hit_rate:.1f}%
🎯 TOP PREDICTIONS: {', '.join(predictions[:4])}

📈 LATEST RESULTS:
{latest_results}

🔗 DASHBOARD: github.com/jorige3/kalyan
💻 Ollama: qwen2.5-coder:1.5b running on port 11434
        """

        # TELEGRAM SETUP (REPLACE WITH YOUR BOT DETAILS)
        bot_token = '8358197339:AAFXYZyCSfX519-g0hVNdVWJVSJKQKLoJ1I'  # From @BotFather
        chat_id = '7975962879'      # Your Telegram chat ID
        
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': report,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Daily Kalyan report sent to Telegram!")
        else:
            print(f"Telegram failed: {response.status_code}")
            
    except Exception as e:
        print(f"Report failed: {e}")

if __name__ == "__main__":
    send_daily_report()
