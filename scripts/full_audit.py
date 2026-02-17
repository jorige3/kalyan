# scripts/full_audit.py
import pandas as pd
from datetime import datetime
df = pd.read_csv('data/kalyan.csv')
today = datetime.now().strftime('%Y-%m-%d')

print(f"🚀 KALYAN FULL AUDIT | {today}")
print(f"📊 Records: {len(df)} | Span: {df.date.min()} → {df.date.max()}")
print(f"🔥 Hot Jodi: {df.jodi.value_counts().head()}")
print(f"❄️ Cold Jodi: {df.jodi.value_counts().tail()}")
print(f"📈 Last 7 days:\n{df.tail(7)}")

# Day-of-week patterns
df['day'] = pd.to_datetime(df.date).dt.day_name()
print(f"📅 By Day:\n{df.groupby('day').jodi.agg(['count','nunique']).sort_values('count',ascending=False)}")

# Open-Close sum patterns
df['sum'] = df.open + df.close
print(f"🔢 Hot Sums: {df['sum'].value_counts().head()}")
