#!/bin/bash
cd /home/kishore/kalyan
source venv/bin/activate
python scripts/scrape_full_chart.py 
python main.py >> logs/daily.log 2>&1      # ← kpred = python main.py!
git add . && git commit -m "Daily update $(date '+%Y-%m-%d')" && git push >> logs/daily.log 2>&1

