#!/bin/bash
cd /home/kishore/kalyan
source venv/bin/activate
kpred >> logs/daily.log 2>&1
python scripts/send_report.py >> logs/daily.log 2>&1
git add . && git commit -m "Daily update $(date '+%Y-%m-%d')" && git push
