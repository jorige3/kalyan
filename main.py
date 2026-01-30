from src.loaders.data_loader import load_data
from src.analysis.cycle_analyzer import calculate_cycle_gaps, identify_due_cycles, identify_hot_numbers, identify_exhausted_numbers
from src.analysis.prediction_engine import get_top_picks
from datetime import datetime
import config

REPORT_FILE = "reports/today_output.txt"


def main():
    df = load_data()
    print("✅ Data loaded")

    report_lines = []
    report_lines.append(f"Sridevi Night Analysis — {datetime.now().date()}")
    report_lines.append("=" * 50)

    print("🔄 Analyzing cycle gaps...")
    # Analyze Jodi cycle gaps
    jodi_cycle_gaps = calculate_cycle_gaps(df, 'jodi')
    
    # Identify hot Jodis
    hot_jodis = identify_hot_numbers(df, 'jodi', config.HOT_LOOKBACK_DAYS, config.HOT_TOP_N)
    print(f"🔥 Hot Jodis: {', '.join(hot_jodis)}")
    report_lines.append(f"🔥 Hot Jodis: {', '.join(hot_jodis)}")

    # Identify due cycles
    due_cycles = identify_due_cycles(jodi_cycle_gaps, config.DUE_TOP_N)
    print(f"🔄 Due Cycles: {', '.join(due_cycles)}")
    report_lines.append(f"🔄 Due Cycles: {', '.join(due_cycles)}")

    # Identify exhausted Jodis
    exhausted_jodis = identify_exhausted_numbers(jodi_cycle_gaps, hot_jodis, config.EXHAUSTED_GAP_THRESHOLD)
    print(f"🚫 Exhausted: {', '.join(exhausted_jodis)}")
    report_lines.append(f"🚫 Exhausted: {', '.join(exhausted_jodis)}")

    # Get today's top picks
    top_picks = get_top_picks(hot_jodis, due_cycles, exhausted_jodis, config.TOP_PICKS_COUNT)
    print(f"🎯 TODAY'S TOP PICKS: {', '.join(top_picks)}")
    report_lines.append(f"🎯 TODAY'S TOP PICKS: {', '.join(top_picks)}")

    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))

    print("📄 Report saved!")


if __name__ == "__main__":
    main()