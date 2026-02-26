import pandas as pd
from datetime import timedelta
from collections import defaultdict

DATA_PATH = "data/kalyan.csv"

def compute_heat_scores(df):
     
    # Recent digit heat (last 30 days)
    recent_digits = recent_df["jodi"].apply(lambda x: list(x))
    digit_series = pd.Series([d for sublist in recent_digits for d in sublist])
    digit_heat = digit_series.value_counts(normalize=True)


    last_seen = df.groupby("jodi")["date"].max()
    days_absent = (df["date"].max() - last_seen).dt.days
    absence_norm = days_absent / days_absent.max()

    heat_scores = {}
    min_frequency_threshold = 10

    for j in df["jodi"].unique():
        total_count = df["jodi"].value_counts().get(j, 0)
        if total_count < min_frequency_threshold:
            continue

        d1 = j[0]
        d2 = j[1]

        digit_score = digit_heat.get(d1, 0) + digit_heat.get(d2, 0)

        score = (rc * 0.7) + (digit_score * 0.2) + (ab * 0.1)

        heat_scores[j] = score

    return sorted(heat_scores.items(), key=lambda x: x[1], reverse=True)


def main():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["jodi"] = df["jodi"].astype(str)
    df = df[df["jodi"].str.len() == 2]
    df = df.sort_values("date")

    end_date = df["date"].max()
    start_date = end_date - timedelta(days=730)
    test_df = df[df["date"] >= start_date]

    total_days = 0
    hits_top10 = 0
    hits_top5 = 0

    results = []  # 🔥 store daily results here

    print("\n🚀 Rolling Backtest (Last 2 Years)")
    print("=" * 50)

    for current_date in test_df["date"].unique():

        train_df = df[df["date"] < current_date]
        actual_row = df[df["date"] == current_date]

        if train_df.shape[0] < 200:
            continue

        heat = compute_heat_scores(train_df)
        top10 = [j for j, _ in heat[:10]]
        top5 = top10[:5]

        actual = actual_row["jodi"].values[0]

        hit10 = actual in top10
        hit5 = actual in top5

        total_days += 1

        if hit10:
            hits_top10 += 1
        if hit5:
            hits_top5 += 1

        # store result
        results.append({
            "date": current_date,
            "hit_top10": hit10,
            "hit_top5": hit5
        })

    print(f"\nTotal Days Tested: {total_days}")
    print(f"Top 10 Hit Rate: {round((hits_top10/total_days)*100,2)}%")
    print(f"Top 5 Hit Rate: {round((hits_top5/total_days)*100,2)}%")

    # 🔥 Yearly Breakdown
    year_stats = defaultdict(lambda: {"days": 0, "top10_hits": 0, "top5_hits": 0})

    for r in results:
        year = pd.to_datetime(r["date"]).year
        year_stats[year]["days"] += 1

        if r["hit_top10"]:
            year_stats[year]["top10_hits"] += 1
        if r["hit_top5"]:
            year_stats[year]["top5_hits"] += 1

    print("\n📊 Yearly Breakdown")
    print("=" * 50)

    for year, stats in sorted(year_stats.items()):
        days = stats["days"]
        t10 = (stats["top10_hits"] / days) * 100
        t5 = (stats["top5_hits"] / days) * 100

        print(f"{year} → Days: {days}")
        print(f"   Top 10: {t10:.2f}%")
        print(f"   Top 5 : {t5:.2f}%\n")

    print("✅ Backtest Complete")


if __name__ == "__main__":
    main()
