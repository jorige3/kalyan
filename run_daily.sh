#!/bin/bash
cd /home/kishore/kalyan
source venv/bin/activate
python main.py >> logs/daily.log 2>&1      # ← kpred = python main.py!
python scripts/send_report.py >> logs/daily.log 2>&1
git add . && git commit -m "Daily update $(date '+%Y-%m-%d')" && git push >> logs/daily.log 2>&1

