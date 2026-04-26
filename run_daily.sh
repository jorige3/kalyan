#!/bin/bash
# Kalyan Daily Analytical Run (Cron-Safe)
# Runs daily analysis at 8 PM via cron

PROJECT_DIR="/home/kishore/kalyan"
cd "$PROJECT_DIR" || exit 1

# Use full venv Python path (cron ignores 'source activate')
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Run analytical workflow with backtest
"$VENV_PYTHON" main.py --backtest-days 60 --force

# Copy kalyan data to MatkaAnalyzerPro (full paths, no tilde)
"$VENV_PYTHON" -c "
import pandas as pd
import sys, os
sys.path.insert(0, '$PROJECT_DIR/src')
df = pd.read_csv('$PROJECT_DIR/data/kalyan.csv')
df[['date','jodi']].to_csv('/home/kishore/MatkaAnalyzerPro/matka_analyzer/data/kalyan.csv', index=False)
print('Data copy completed')
"

# Log completion timestamp
echo "$(date): Daily run completed" >> "$PROJECT_DIR/logs/daily_run.log"
