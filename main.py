import sys
from pathlib import Path
from datetime import datetime
import argparse

import config
from src.data.loader import DataLoader
from src.models.heat_model import HeatModel
from src.backtest.rolling_backtester import RollingBacktester
from src.reporting.report_generator import ReportGenerator
from src.reporting.telegram_sender import TelegramSender
from src.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    parser = argparse.ArgumentParser(description="Kalyan Market Prediction System")
    parser.add_argument("--force", action="store_true", help="Force execution even if report exists")
    parser.add_argument("--no-telegram", action="store_true", help="Do not send telegram message")
    parser.add_argument("--backtest-days", type=int, default=config.BACKTEST_WINDOW_DAYS, help="Number of days for backtest")
    args = parser.parse_args()

    today_str = datetime.now().strftime("%Y-%m-%d")
    report_path = Path(config.REPORTS_DIR) / f"kalyan_report_{today_str}.txt"

    if report_path.exists() and not args.force:
        logger.info(f"Report for {today_str} already exists. Skipping execution. Use --force to override.")
        return

    logger.info("Starting Kalyan Analytical Workflow")

    # 1. Load Data
    loader = DataLoader(config.DATA_CSV_PATH)
    try:
        df = loader.load_data()
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        sys.exit(1)

    # 2. Initialize Model
    model = HeatModel(
        recent_window=config.RECENT_WINDOW, 
        long_term_window=config.LONG_TERM_WINDOW
    )

    # 3. Run Rolling Backtest (to get historical hit rate)
    logger.info("Running rolling backtest to evaluate model confidence...")
    backtester = RollingBacktester(model, window_days=args.backtest_days)
    backtest_metrics = backtester.run(df)

    # 4. Generate Predictions for today
    logger.info("Generating predictions for today...")
    predictions = model.predict(df)

    # 5. Generate Report
    logger.info("Generating report...")
    report_gen = ReportGenerator(config.REPORTS_DIR)
    report_str = report_gen.generate_report(predictions, backtest_metrics)

    # 6. Send Telegram Notification
    if not args.no_telegram:
        logger.info("Sending Telegram notification...")
        sender = TelegramSender()
        sender.send_message(report_str)

    logger.info("Workflow completed successfully.")

if __name__ == "__main__":
    main()
