import argparse
import logging
import os
from datetime import datetime
from typing import Dict, List

from fpdf import FPDF  # Using fpdf2 for PDF generation

import config
from src.analysis.hot_cold import HotColdAnalyzer
from src.analysis.trend_window import TrendWindowAnalyzer
from src.engine.kalyan_engine import KalyanEngine

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

        # Perform analysis
        analysis_results = {
            "hot_digits": hot_cold_analyzer.get_hot_digits(),
            "hot_jodis": hot_cold_analyzer.get_hot_jodis(),
            "due_cycles": hot_cold_analyzer.get_due_cycles()['due_jodis'],
            "exhausted_numbers": hot_cold_analyzer.get_exhausted_numbers()['exhausted_jodis'],
            "trend_due_jodis": trend_analyzer.get_due_cycles_by_last_appearance()['due_jodis'],
            "trend_exhausted_jodis": trend_analyzer.get_exhausted_numbers_by_streak()['exhausted_jodis'],
        }

        # Print analysis results in the new format
        current_date = datetime.now().strftime('%Y-%m-%d')
        print(f"Kalyan Analysis — {current_date}")

        hot_digit_display = analysis_results['hot_digits'][0] if analysis_results['hot_digits'] else 'N/A'
        print(f"Hot Digit: 🔥 {hot_digit_display}")

        hot_jodis_display = ', '.join(analysis_results['hot_jodis']) if analysis_results['hot_jodis'] else 'N/A'
        print(f"🔥 Hot Jodis: {hot_jodis_display}")

        due_cycles_display = ', '.join(analysis_results['due_cycles']) if analysis_results['due_cycles'] else 'N/A'
        print(f"🔄 Due Cycles (Hot/Cold): {due_cycles_display}")

        exhausted_display = ', '.join(analysis_results['exhausted_numbers']) if analysis_results['exhausted_numbers'] else 'N/A'
        print(f"🚫 Exhausted (Hot/Cold): {exhausted_display}")

        trend_due_jodis_display = ', '.join(analysis_results['trend_due_jodis']) if analysis_results['trend_due_jodis'] else 'N/A'
        print(f"🔄 Due Cycles (Trend): {trend_due_jodis_display}")

        trend_exhausted_jodis_display = ', '.join(analysis_results['trend_exhausted_jodis']) if analysis_results['trend_exhausted_jodis'] else 'N/A'
        print(f"🚫 Exhausted (Trend): {trend_exhausted_jodis_display}")

        # Get top picks
        top_picks = engine.get_top_picks(analysis_results)
        top_picks_display = ', '.join(top_picks) if top_picks else 'N/A'
        print(f"🎯 TODAY'S TOP PICKS: {top_picks_display}")

        # Prepare report lines for PDF
        report_lines = [
            f"Kalyan Analysis — {current_date}",
            f"Hot Digit: 🔥 {hot_digit_display}",
            f"🔥 Hot Jodis: {hot_jodis_display}",
            f"🔄 Due Cycles (Hot/Cold): {due_cycles_display}",
            f"🚫 Exhausted (Hot/Cold): {exhausted_display}",
            f"🔄 Due Cycles (Trend): {trend_due_jodis_display}",
            f"🚫 Exhausted (Trend): {trend_exhausted_jodis_display}",
            f"🎯 TODAY'S TOP PICKS: {top_picks_display}"
        ]

        pdf_output_path = f"reports/kalyan_analysis_{analysis_date.strftime('%Y-%m-%d')}.pdf"

        if os.path.exists(pdf_output_path):
            logging.info(f"📄 PDF Report for {analysis_date.date()} already exists at {pdf_output_path}. Skipping generation.")
        else:
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

            pdf.output(pdf_output_path)
            logging.info(f"📄 PDF Report saved to {pdf_output_path}")

    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)

if __name__ == "__main__":
    main()
