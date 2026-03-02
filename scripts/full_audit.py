# scripts/full_audit.py

from datetime import datetime

import pandas as pd

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv("data/kalyan.csv")

print("\n" + "="*60)
print(f"🚀 KALYAN FULL AUDIT | {datetime.now().strftime('%d-%b-%Y')}")
print("="*60)

# ==============================
# BASIC CLEANING
# ==============================

# Ensure required columns exist
required_cols = ["date", "jodi"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column: {col}")

# Clean date column
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Clean jodi column
df["jodi"] = df["jodi"].astype(str).str.zfill(2)

# Derive open/close safely
df["open"] = df["jodi"].str[0].astype(int)
df["close"] = df["jodi"].str[1].astype(int)

# ==============================
# DATA SUMMARY
# ==============================

print(f"\n📊 Total Records : {len(df)}")
print(f"📅 Date Span     : {df['date'].min().date()} → {df['date'].max().date()}")

# ==============================
# HOT / COLD JODI
# ==============================

jodi_counts = df["jodi"].value_counts()

print("\n🔥 TOP 5 HOT JODI")
print(jodi_counts.head())

print("\n❄️ TOP 5 COLD JODI")
print(jodi_counts.tail())

# ==============================
# LAST 7 DAYS SNAPSHOT
# ==============================

print("\n📈 LAST 7 DAYS")
print(df.sort_values("date").tail(7)[["date", "jodi"]])

# ==============================
# DAY OF WEEK PATTERNS
# ==============================

df["day"] = df["date"].dt.day_name()

print("\n📅 PERFORMANCE BY DAY")
day_stats = (
    df.groupby("day")["jodi"]
    .agg(["count", "nunique"])
    .sort_values("count", ascending=False)
)

print(day_stats)

# ==============================
# SUM INTELLIGENCE
# ==============================

df["sum"] = df["open"] + df["close"]

print("\n🔢 HOT SUMS")
print(df["sum"].value_counts().head())

print("\n🔢 COLD SUMS")
print(df["sum"].value_counts().tail())

# ==============================
# DIGIT INTELLIGENCE
# ==============================

all_digits = pd.concat([df["open"], df["close"]])
digit_counts = all_digits.value_counts().sort_index()

print("\n🔎 DIGIT FREQUENCY (ALL TIME)")
for digit, count in digit_counts.items():
    print(f"Digit {digit}: {count}")

print("\n" + "="*60)
print("✅ FULL AUDIT COMPLETE")
print("="*60 + "\n")

df = df[df["jodi"].str.len() == 2]

# ==============================
# 🔥 HEAT SCORE RANKING SYSTEM
# ==============================

print("\n🔥 HEAT SCORE RANKING (TOP 10)")

# Sort by date just in case
df = df.sort_values("date")

# Last 30 days slice
last_30 = df.tail(30)

# Long-term frequency (normalized)
long_term = df["jodi"].value_counts(normalize=True)

# Recent frequency (normalized)
recent = last_30["jodi"].value_counts(normalize=True)

# Absence gap calculation
last_seen = df.groupby("jodi")["date"].max()
days_absent = (df["date"].max() - last_seen).dt.days

# Normalize absence (higher absence → higher boost)
absence_norm = days_absent / days_absent.max()

heat_scores = {}

min_frequency_threshold = 10  # ignore ultra-rare noise

for j in df["jodi"].unique():
    total_count = df["jodi"].value_counts().get(j, 0)

    if total_count < min_frequency_threshold:
        continue  # skip weak historical numbers

    lt = long_term.get(j, 0)
    rc = recent.get(j, 0)
    ab = absence_norm.get(j, 0)

    # Reduce absence weight
    score = (lt * 0.5) + (rc * 0.4) + (ab * 0.1)

    heat_scores[j] = round(score, 4)

# Convert to DataFrame
heat_df = (
    pd.DataFrame.from_dict(heat_scores, orient="index", columns=["HeatScore"])
    .sort_values("HeatScore", ascending=False)
)

print(heat_df.head(10))
