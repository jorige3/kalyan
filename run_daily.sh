#!/bin/bash
# Kalyan Daily Analytical Run
# This script orchestrates the daily data analysis and reporting.

PROJECT_DIR="/home/kishore/kalyan"
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the analytical workflow
# --force: override existing report for today
# --backtest-days: evaluate model on recent performance
python3 main.py --backtest-days 60 --force

# Optional: Automatic commit of the daily report
# git add reports/*.txt logs/*.log
# git commit -m "Daily Analytical Report - $(date '+%Y-%m-%d')"
# git push
python -c "import pandas as pd; df=pd.read_csv('~/kalyan/data/kalyan.csv'); df[['date','jodi']].to_csv('~/MatkaAnalyzerPro/matka_analyzer/data/kalyan.csv',index=False)"
