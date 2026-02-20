# Track prediction accuracy
import glob
import os
import re

import pandas as pd

df = pd.read_csv('data/kalyan.csv')
latest_pred = max(glob.glob('reports/kalyan_analysis_*.json'), key=os.path.getctime)

with open(latest_pred) as f:
    preds = re.findall(r'(\d{2}) \([A-Z]', f.read())  # 96,11,79...
    
print(f"🎯 Yesterday's predictions: {preds}")
print("📊 Tomorrow's actual vs pred → Track hit rate!")
