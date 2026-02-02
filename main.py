import argparse
import logging
import pandas as pd
from datetime import datetime
from fpdf import FPDF # Using fpdf2 for PDF generation

from src.engine.kalyan_engine import KalyanEngine
from src.analysis.hot_cold import HotColdAnalyzer
from src.analysis.trend_window import TrendWindowAnalyzer
import config
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Unicode font
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSansCondensed-Bold.ttf", uni=True)
        self.set_font('DejaVu', '', 15) # Set default font to DejaVu

    def header(self):
        self.set_font('DejaVu', 'B', 15)
        self.cell(0, 10, f"Kalyan Analysis Report - {datetime.now().strftime('%Y-%m-%d')}", new_x='LMARGIN', new_y='NEXT', align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', new_x='RIGHT', new_y='TOP', align='C')

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT', align='L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

    def add_table(self, data, col_width=40):
        self.set_font('DejaVu', 'B', 10)
        for header in data[0]:
            self.cell(col_width, 7, str(header), 1, 0, 'C')
        self.ln()
        self.set_font('DejaVu', '', 10)
        for row in data[1:]:
            for item in row:
                self.cell(col_width, 7, str(item), 1, 0, 'C')
            self.ln()
        self.ln(5)

def run_monte_carlo_simulation(predictions: List[str], num_simulations: int = 1000) -> Dict[str, float]:
    """
    Placeholder for Monte Carlo simulation to assess prediction confidence.
    In a real scenario, this would simulate outcomes based on historical probabilities
    and return confidence scores for each prediction.
    """
    logging.info(f"Running Monte Carlo simulations for {predictions}...")
    confidence_scores = {pred: 0.0 for pred in predictions}
    # Dummy simulation: assign random confidence for demonstration
    import random
    for pred in predictions:
        confidence_scores[pred] = round(random.uniform(0.5, 0.95), 2)
    return confidence_scores

def main():
    parser = argparse.ArgumentParser(description="Kalyan Matka Predictive Analytics")
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='Date for analysis (YYYY-MM-DD). Defaults to today.')
    parser.add_argument('--csv', type=str, default='data/kalyan.csv',
                        help='Path to the historical Kalyan data CSV file.')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output for detailed analysis.')
    args = parser.parse_args()

    analysis_date = datetime.strptime(args.date, '%Y-%m-%d')
    logging.info(f"Starting Kalyan analysis for {analysis_date.date()}...")

    try:
        engine = KalyanEngine(data_path=args.csv)
        df = engine.get_historical_data()
        if df.empty:
            logging.warning("No historical data available after loading. Cannot perform analysis.")
            return

        hot_cold_analyzer = HotColdAnalyzer(df)
        trend_analyzer = TrendWindowAnalyzer(df)

        report_lines = []
        report_lines.append(f"Kalyan Analysis - {analysis_date.date()}")
        report_lines.append("=" * 50)

        # --- Hot/Cold Analysis ---
        logging.info("Performing Hot/Cold analysis...")
        hot_digits = hot_cold_analyzer.get_hot_digits(config.HOT_LOOKBACK_DAYS, config.HOT_TOP_N)
        cold_digits = hot_cold_analyzer.get_cold_digits(config.HOT_LOOKBACK_DAYS, config.EXHAUSTED_BOTTOM_N)
        hot_jodis = hot_cold_analyzer.get_hot_jodis(config.HOT_LOOKBACK_DAYS, config.HOT_TOP_N)
        cold_jodis = hot_cold_analyzer.get_cold_jodis(config.HOT_LOOKBACK_DAYS, config.EXHAUSTED_BOTTOM_N)

        report_lines.append(f"🔥 Hot Digits (last {config.HOT_LOOKBACK_DAYS} days): {', '.join(map(str, hot_digits))}")
        report_lines.append(f"🧊 Cold Digits (last {config.HOT_LOOKBACK_DAYS} days): {', '.join(map(str, cold_digits))}")
        report_lines.append(f"🔥 Hot Jodis (last {config.HOT_LOOKBACK_DAYS} days): {', '.join(hot_jodis)}")
        report_lines.append(f"🧊 Cold Jodis (last {config.HOT_LOOKBACK_DAYS} days): {', '.join(cold_jodis)}")
        report_lines.append("-" * 50)

        # --- Due Cycles & Exhausted Numbers ---
        logging.info("Identifying Due Cycles and Exhausted Numbers...")
        due_cycles_data = trend_analyzer.get_due_cycles_by_last_appearance(config.DUE_THRESHOLD, config.CYCLE_GAP_MAX_DAYS)
        due_jodis = due_cycles_data.get("due_jodis", [])
        due_digits = due_cycles_data.get("due_digits", [])

        exhausted_data = trend_analyzer.get_exhausted_numbers_by_streak(config.EXHAUSTED_LOOKBACK_DAYS, config.EXHAUSTED_GAP_THRESHOLD + 1) # +1 because threshold is 0
        exhausted_jodis = exhausted_data.get("exhausted_jodis", [])
        exhausted_digits = exhausted_data.get("exhausted_digits", [])

        report_lines.append(f"⏰ Due Jodis (not seen in {config.CYCLE_GAP_MAX_DAYS} days): {', '.join(due_jodis)}")
        report_lines.append(f"⏰ Due Digits (not seen in {config.CYCLE_GAP_MAX_DAYS} days): {', '.join(map(str, due_digits))}")
        report_lines.append(f"🚫 Exhausted Jodis (seen {config.EXHAUSTED_GAP_THRESHOLD + 1}+ times in {config.EXHAUSTED_LOOKBACK_DAYS} days): {', '.join(exhausted_jodis)}")
        report_lines.append(f"🚫 Exhausted Digits (seen {config.EXHAUSTED_GAP_THRESHOLD + 1}+ times in {config.EXHAUSTED_LOOKBACK_DAYS} days): {', '.join(map(str, exhausted_digits))}")
        report_lines.append("-" * 50)

        # --- Top Picks (Simplified for now) ---
        logging.info("Generating Top Picks...")
        # This is a simplified logic. A real prediction engine would combine these factors intelligently.
        potential_picks = list(set(hot_jodis + due_jodis))
        if not potential_picks:
            potential_picks = hot_jodis # Fallback if no due jodis

        # Filter out exhausted jodis from potential picks
        final_picks = [p for p in potential_picks if p not in exhausted_jodis]
        
        # Limit to TOP_PICKS_COUNT
        top_picks = final_picks[:config.TOP_PICKS_COUNT]
        if not top_picks and df is not None and not df.empty:
            # Fallback to top hot jodis if no other picks
            top_picks = hot_jodis[:config.TOP_PICKS_COUNT]
        elif not top_picks:
            top_picks = ["N/A"] # No picks if no data

        report_lines.append(f"🎯 TODAY'S TOP PICKS: {', '.join(top_picks)}")
        report_lines.append("-" * 50)

        # --- Monte Carlo Simulation for Confidence ---
        if top_picks and top_picks != ["N/A"]:
            confidence_scores = run_monte_carlo_simulation(top_picks)
            report_lines.append("📊 Prediction Confidence (Monte Carlo):")
            for pick, score in confidence_scores.items():
                report_lines.append(f"  - {pick}: {score*100:.2f}%")
            report_lines.append("-" * 50)

        # --- Console Output ---
        for line in report_lines:
            print(line)

        # --- PDF Report Generation ---
        pdf = PDFReport()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.chapter_title(f"Kalyan Analysis Report - {analysis_date.date()}")
        pdf.chapter_body("\n".join(report_lines))

        # Example of adding a table (e.g., for digit frequencies)
        if args.verbose:
            digit_freq_data = hot_cold_analyzer.get_digit_frequency(config.HOT_LOOKBACK_DAYS)
            if not digit_freq_data.empty:
                pdf.chapter_title("Digit Frequencies (Last 30 Days)")
                table_data = [['Digit', 'Frequency']]
                for digit, freq in digit_freq_data.items():
                    table_data.append([digit, freq])
                pdf.add_table(table_data, col_width=30)

        pdf_output_path = f"reports/kalyan_analysis_{analysis_date.strftime('%Y-%m-%d')}.pdf"
        pdf.output(pdf_output_path)
        logging.info(f"📄 PDF Report saved to {pdf_output_path}")

    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)

if __name__ == "__main__":
    main()
