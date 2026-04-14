import argparse
import sys
from datetime import datetime
from pathlib import Path

import config
from scripts.scrape_kalyan import scrape_kalyan
from src.backtest.rolling_backtester import RollingBacktester
from src.data.loader import DataLoader
from src.models.ensemble_model import EnsembleModel
from src.models.heat_model import HeatModel
from src.models.matrix_model import MatrixModel
from src.models.momentum_model import MomentumModel
from src.reporting.report_generator import ReportGenerator
from src.reporting.telegram_sender import TelegramSender
from src.utils.logger import setup_logger

logger = setup_logger("main")


def get_confidence_score(hit_rate):
    """Maps hit rate to a 1-10 confidence score."""
    if hit_rate >= 0.25:
        return "10/10"
    if hit_rate >= 0.20:
        return "9/10"
    if hit_rate >= 0.15:
        return "8/10"
    if hit_rate >= 0.12:
        return "7/10"
    if hit_rate >= 0.10:
        return "6/10"
    if hit_rate >= 0.08:
        return "5/10"
    if hit_rate >= 0.05:
        return "4/10"
    if hit_rate >= 0.03:
        return "3/10"
    return "2/10"


def main():
    parser = argparse.ArgumentParser(description="Kalyan Quantitative Ensemble System")
    parser.add_argument(
        "--model", type=str, default=config.MODEL_TYPE, help="Model type: heat, matrix, ensemble"
    )
    parser.add_argument(
        "--backtest-days", type=int, default=config.BACKTEST_WINDOW_DAYS, help="Days for backtest"
    )
    parser.add_argument("--force", action="store_true", help="Force run even if report exists")
    parser.add_argument(
        "--scrape", action="store_true", default=True, help="Run scraper before analysis"
    )
    parser.add_argument("--no-scrape", action="store_false", dest="scrape", help="Skip scraper")
    args = parser.parse_args()

    # 0. Check if report already exists for today
    file_date = datetime.now().strftime("%Y-%m-%d")
    report_path = Path(config.REPORTS_DIR) / f"kalyan_report_{file_date}.txt"
    if report_path.exists() and not args.force:
        logger.info(
            f"Report for {file_date} already exists. Skipping execution. Use --force to override."
        )
        return

    logger.info(f"Starting Kalyan Analysis Workflow [Model: {args.model}]")

    # 1. Scrape data if requested
    if args.scrape:
        logger.info("Running scraper...")
        try:
            scrape_kalyan()
        except Exception as e:
            logger.error(f"Scraper failed: {e}. Proceeding with existing data.")

    # 2. Load Data
    loader = DataLoader(config.DATA_CSV_PATH)
    try:
        df = loader.load_data()
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        sys.exit(1)

    # 3. Initialize Models
    heat_model = HeatModel(
        recent_window=config.RECENT_WINDOW, long_term_window=config.LONG_TERM_WINDOW
    )
    matrix_model = MatrixModel(window=config.MATRIX_WINDOW_DAYS)
    momentum_model = MomentumModel(window=config.MOMENTUM_WINDOW)

    # 4. Select Model
    if args.model == "heat":
        selected_model = heat_model
    elif args.model == "matrix":
        selected_model = matrix_model
    else:
        selected_model = EnsembleModel(
            heat_model=heat_model,
            matrix_model=matrix_model,
            momentum_model=momentum_model,
            weights=config.ENSEMBLE_WEIGHTS,
        )

    # 5. Run Backtest (Last 365 days for confidence)
    logger.info(f"Evaluating model confidence via {args.backtest_days}-day rolling backtest...")
    backtester = RollingBacktester(selected_model, window_days=args.backtest_days)
    metrics = backtester.run(df)

    hit_rate = metrics.get("hit_rate_top_10", 0)
    confidence = get_confidence_score(hit_rate)

    # 6. Generate Predictions for today
    logger.info("Generating final predictions...")
    predictions = selected_model.predict(df)

    # 7. Generate and Save Report
    logger.info("Generating report...")
    report_gen = ReportGenerator(output_dir=config.REPORTS_DIR)
    report_text = report_gen.generate_report(predictions, metrics)

    # 8. Send Telegram Notification
    logger.info("Sending Telegram notification...")
    telegram = TelegramSender()
    telegram.send_message(report_text)

    # 9. Console Output
    top_5 = predictions.head(5)["jodi"].tolist()
    top_10 = predictions.head(10)["jodi"].tolist()

    print("\n" + "=" * 40)
    print(f"KALYAN {args.model.upper()} ANALYSIS")
    print("=" * 40)
    print("\nTop 5:")
    print(", ".join(top_5))
    print("\nTop 10:")
    print(", ".join(top_10))
    print(f"\nConfidence: {confidence}")
    print("=" * 40 + "\n")

    logger.info("Workflow completed successfully.")


if __name__ == "__main__":
    main()
