import pandas as pd
from datetime import datetime
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportGenerator:
    """Generates prediction reports and analysis summaries."""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_report(self, predictions: pd.DataFrame, backtest_metrics: dict) -> str:
        """
        Creates a text summary of predictions.
        Confidence is derived from historical hit rate.
        """
        if predictions.empty:
            return "No predictions available."
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        top_5 = predictions.head(5)
        top_10 = predictions.head(10)
        
        hit_rate_top_5 = backtest_metrics.get('hit_rate_top_5', 0)
        hit_rate_top_10 = backtest_metrics.get('hit_rate_top_10', 0)
        
        # Confidence score derived from historical hit rate
        # For example, (hit_rate_top_5 * 100) / 10
        confidence_score = min(10, round(hit_rate_top_5 * 50)) # 20% hit rate = 10/10
        
        report = []
        report.append("=" * 40)
        report.append(f"KALYAN ANALYTICAL REPORT - {now}")
        report.append("=" * 40)
        report.append(f"Historical Hit Rate (Top 5): {hit_rate_top_5:.2%}")
        report.append(f"Historical Hit Rate (Top 10): {hit_rate_top_10:.2%}")
        report.append(f"Confidence Score: {confidence_score}/10")
        report.append("-" * 40)
        report.append("TOP 5 JODI PICKS:")
        for idx, row in top_5.iterrows():
            report.append(f"{row['rank']}. Jodi: {row['jodi']} (Score: {row['score']:.4f})")
        report.append("-" * 40)
        report.append("TOP 10 JODI PICKS:")
        for idx, row in top_10.iterrows():
            report.append(f"{row['rank']}. Jodi: {row['jodi']}")
        report.append("-" * 40)
        report.append("Analysis based on Heat Score Model.")
        report.append("=" * 40)
        
        report_str = "\n".join(report)
        
        # Save to file
        file_date = datetime.now().strftime("%Y-%m-%d")
        file_path = self.output_dir / f"kalyan_report_{file_date}.txt"
        with open(file_path, "w") as f:
            f.write(report_str)
            
        logger.info(f"Report saved to {file_path}")
        return report_str
