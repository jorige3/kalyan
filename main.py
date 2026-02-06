import argparse
import logging
import os
import config
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
import hashlib
import json
from fpdf import FPDF  # Using fpdf2 for PDF generation
from src.analysis.hot_cold import HotColdAnalyzer
from src.analysis.trend_window import TrendWindowAnalyzer
from src.engine.kalyan_engine import KalyanEngine
from src.ux.text_templates import ReportText

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_list(items, limit=15):
    if not items:
        return "N/A"
    if len(items) > limit:
        return ", ".join(items[:limit]) + f" ... (+{len(items)-limit} more)"
    return ", ".join(items)

class PDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Unicode font
        FONTS_DIR = BASE_DIR / "fonts"
        self.add_font("DejaVu", "", str(FONTS_DIR / "DejaVuSans.ttf"), uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSansCondensed-Bold.ttf", uni=True)
        self.set_font('DejaVu', '', 15) # Set default font to DejaVu

    def header(self):
        self.set_font('DejaVu', 'B', 15)
        title = f"{ReportText.PDF_HEADER_TITLE} - {datetime.now().strftime(ReportText.DATE_FORMAT)}"
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT', align='C')
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

    def summary_body(self, body):
        """ Renders a body string with support for **bold** text. """
        self.set_font('', '', 10) # Reset to normal before parsing
        parts = body.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Text inside **
                self.set_font('', 'B')
                self.write(5, part)
                self.set_font('', '') # Reset to normal after bold
            else: # Regular text
                self.write(5, part)
        self.ln()
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

        def format_list(items, limit=15):
            if not items:
                return "N/A"
            if len(items) > limit:
                return ", ".join(items[:limit]) + f" ... (+{len(items)-limit} more)"
            return ", ".join(items)


def generate_daily_summary_and_confidence(analysis_results: Dict) -> Dict:
    """
    Synthesizes raw analysis results into a high-level summary and confidence scores.
    """
    # --- 1. Confidence Scoring for Jodis ---
    all_jodis = set(analysis_results['hot_jodis']) | set(analysis_results['due_cycles']) | set(analysis_results['trend_due_jodis'])
    
    scored_jodis = []
    for jodi in all_jodis:
        score = 0
        reasons = []
        
        # Positive signals
        if jodi in analysis_results['hot_jodis']:
            score += 1
            reasons.append("High Frequency")
        if jodi in analysis_results['trend_due_jodis']:
            score += 1
            reasons.append("Trend-Aligned")
        if jodi in analysis_results['due_cycles']:
            score += 0.5
            reasons.append("Extended Absence")
            
        # Negative signals (Contradictions)
        if jodi in analysis_results['exhausted_numbers']:
            score -= 2 # Heavy penalty for being exhausted
            reasons.append("Exhausted Pattern")
        
        confidence = ReportText.CONFIDENCE_LOW
        if score >= 2:
            confidence = ReportText.CONFIDENCE_HIGH
        elif score >= 1:
            confidence = ReportText.CONFIDENCE_MEDIUM

        scored_jodis.append({
            "jodi": jodi,
            "score": score,
            "confidence": confidence,
            "reasons": reasons
        })

    # Sort by score to find top picks
    scored_jodis.sort(key=lambda x: x['score'], reverse=True)
    
    # --- 2. Determine Strongest Signals and Caution Areas ---
    strongest_signals_formatted = []
    for j in scored_jodis:
        if j['confidence'] == ReportText.CONFIDENCE_HIGH:
            strongest_signals_formatted.append({"type": "jodi", "value": j['jodi'], "confidence": j['confidence']})
    
    # Add hot digit as a strong signal
    if analysis_results['hot_digits']:
        strongest_signals_formatted.insert(0, {"type": "digit", "value": analysis_results['hot_digits'][0], "confidence": ReportText.CONFIDENCE_HIGH})

    caution_areas_formatted = []
    for j in scored_jodis:
        if "Exhausted Pattern" in j['reasons'] and j['score'] > 0:
            caution_areas_formatted.append({"value": j['jodi'], "reason": "Contradictory signal"})
    
    # --- 3. Determine Market Mood and Confidence Score ---
    num_high_confidence = len([j for j in scored_jodis if j['confidence'] == ReportText.CONFIDENCE_HIGH])
    num_medium_confidence = len([j for j in scored_jodis if j['confidence'] == ReportText.CONFIDENCE_MEDIUM])
    
    market_mood = "Quiet"
    if num_high_confidence > 0 or num_medium_confidence > 2:
        market_mood = "Active"
    elif num_medium_confidence > 0:
        market_mood = "Neutral"

    # Calculate confidence score (1-10)
    confidence_score = 3 # Base score
    if market_mood == "Active":
        confidence_score = 7 + num_high_confidence
    elif market_mood == "Neutral":
        confidence_score = 5
    
    confidence_score = min(confidence_score, 10) # Cap at 10

    return {
        "market_mood": market_mood,
        "strongest_signals": strongest_signals_formatted[:3], # Top 3
        "caution_areas": caution_areas_formatted[:3],
        "analytical_confidence_score": confidence_score,
        "top_picks_with_confidence": scored_jodis[:5] # Top 5 for detailed list
    }


def hash_file(path: str) -> str:
    """Generates a SHA256 hash of a file's content."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except FileNotFoundError:
        return "FILE_NOT_FOUND"
    return h.hexdigest()

def write_analysis_snapshot(
    output_path: Path,
    analysis_date: datetime,
    summary: Dict,
    ranked_picks: List[Dict],
    df_record_count: int,
    csv_path: Path,
) -> None:
    """
    Writes a JSON snapshot of the analysis results for reproducibility.
    """
    snapshot = {
        "analysis_date": analysis_date.strftime("%Y-%m-%d"),
        "engine_version": ReportText.VERSION, # Using ReportText.VERSION as config.__version__ is not defined
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "data": {
            "source_file": str(csv_path),
            "record_count": df_record_count,
            "sha256": hash_file(str(csv_path)),
        },

        "daily_summary": summary,
        "ranked_picks": ranked_picks,
    }

    try:
        with open(output_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        logging.info(f"📊 Analysis snapshot saved to {output_path}")
    except IOError as e:
        logging.error(f"Failed to write analysis snapshot to {output_path}: {e}")


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
    parser = argparse.ArgumentParser(description=ReportText.PROJECT_TITLE)
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

        # --- Synthesize Analysis into a Summary ---
        summary_data = generate_daily_summary_and_confidence(analysis_results)
        top_picks_with_confidence = summary_data.get('top_picks_with_confidence', [])
        top_picks_display = ', '.join([f"{pick['jodi']} ({pick['confidence']})" for pick in top_picks_with_confidence]) if top_picks_with_confidence else 'N/A'

        # --- Write Analysis Snapshot ---
        json_path = REPORTS_DIR / f"kalyan_analysis_{analysis_date.strftime('%Y-%m-%d')}.json"
        write_analysis_snapshot(
            output_path=json_path,
            analysis_date=analysis_date,
            summary={
                "market_mood": summary_data['market_mood'],
                "confidence_score": summary_data['analytical_confidence_score'],
                "strongest_signals": summary_data['strongest_signals'],
                "areas_for_caution": summary_data['caution_areas'],
            },
            ranked_picks=[
                {"rank": i + 1, "value": pick['jodi'], "confidence": pick['confidence']}
                for i, pick in enumerate(top_picks_with_confidence)
            ],
            df_record_count=len(df),
            csv_path=Path(args.csv),
        )

        # --- Console Output Section ---
        print("=" * 60)
        print(f"  {ReportText.CONSOLE_HEADER_TITLE} | Date: {analysis_date.strftime(ReportText.DATE_FORMAT)} | v{ReportText.VERSION}")
        print("=" * 60)
        
        # --- New Summary Output ---
        print(f"{ReportText.SUMMARY_MOOD:<28}: {summary_data['market_mood']}")
        print(f"{ReportText.SUMMARY_CONFIDENCE:<28}: {summary_data['analytical_confidence_score']}/10")
        
        strongest_signals_console = [f"{s['value']} ({s['confidence']})" for s in summary_data['strongest_signals']]
        print(f"{ReportText.SUMMARY_STRONGEST_SIGNALS:<28}: {', '.join(strongest_signals_console) if strongest_signals_console else 'N/A'}")
        
        caution_areas_console = [f"{s['value']} ({s['reason']})" for s in summary_data['caution_areas']]
        print(f"{ReportText.SUMMARY_CAUTION_AREAS:<28}: {', '.join(caution_areas_console) if caution_areas_console else 'None'}")

        print("-" * 60)
        print(f"{ReportText.PICKS_SECTION_TITLE:<28}: {top_picks_display}")
        print("-" * 60)
        
        if args.verbose:
            print("--- Detailed Analysis Breakdown ---")
            hot_digit_display = analysis_results['hot_digits'][0] if analysis_results['hot_digits'] else 'N/A'
            print(f"{ReportText.HIGH_FREQUENCY_DIGITS:<25}: {hot_digit_display}")
            hot_jodis_display = ', '.join(analysis_results['hot_jodis'][:5]) if analysis_results['hot_jodis'] else 'N/A'
            print(f"{ReportText.HIGH_FREQUENCY_JODIS:<25}: {hot_jodis_display}")
            due_cycles_display = ", ".join(sorted(analysis_results['due_cycles'], key=int)[:5]) if analysis_results['due_cycles'] else 'N/A'
            print(f"{ReportText.EXTENDED_ABSENCE_JODIS:<25}: {due_cycles_display}")
            exhausted_display = ', '.join(analysis_results['exhausted_numbers'][:5]) if analysis_results['exhausted_numbers'] else 'N/A'
            print(f"{ReportText.EXHAUSTED_JODIS:<25}: {exhausted_display}")
            print("-" * 60)

        # --- PDF Report Generation ---
        pdf_output_path = REPORTS_DIR / f"kalyan_analysis_{analysis_date.strftime('%Y-%m-%d')}.pdf"

        if os.path.exists(pdf_output_path):
            logging.info(f"📄 PDF Report for {analysis_date.date()} already exists at {pdf_output_path}. Skipping generation.")
        else:
            pdf = PDFReport()
            pdf.alias_nb_pages()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # --- Daily Summary Section ---
            pdf.chapter_title(ReportText.SUMMARY_SECTION_TITLE)
            
            strongest_signals_pdf = [f"{s['value']} ({s['confidence']})" for s in summary_data['strongest_signals']]
            caution_areas_pdf = [f"{s['value']} ({s['reason']})" for s in summary_data['caution_areas']]

            summary_body_pdf = (
                f"**{ReportText.SUMMARY_MOOD}:** {summary_data['market_mood']}\n"
                f"**{ReportText.SUMMARY_CONFIDENCE}:** {summary_data['analytical_confidence_score']}/10\n"
                f"**{ReportText.SUMMARY_STRONGEST_SIGNALS}:** {', '.join(strongest_signals_pdf) if strongest_signals_pdf else 'N/A'}\n"
                f"**{ReportText.SUMMARY_CAUTION_AREAS}:** {', '.join(caution_areas_pdf) if caution_areas_pdf else 'None'}"
            )
            pdf.summary_body(summary_body_pdf)

            # --- Top Picks Section ---
            pdf.chapter_title(ReportText.PICKS_SECTION_TITLE)
            pdf.chapter_body(f"Top 5 Analytical Picks: {top_picks_display}")

            # --- Detailed Analysis Section (for verbose PDF) ---
            if args.verbose:
                pdf.chapter_title(ReportText.DETAILED_ANALYSIS_SECTION_TITLE)
                hot_digit_display = analysis_results['hot_digits'][0] if analysis_results['hot_digits'] else 'N/A'
                hot_jodis_display = ', '.join(analysis_results['hot_jodis'][:5]) if analysis_results['hot_jodis'] else 'N/A'
                due_cycles_display = ", ".join(sorted(analysis_results['due_cycles'], key=int)[:5]) if analysis_results['due_cycles'] else 'N/A'
                exhausted_display = ', '.join(analysis_results['exhausted_numbers'][:5]) if analysis_results['exhausted_numbers'] else 'N/A'
                analysis_body = (
                    f"**{ReportText.HIGH_FREQUENCY_DIGITS}:** {hot_digit_display}\n"
                    f"**{ReportText.HIGH_FREQUENCY_JODIS}:** {hot_jodis_display}\n"
                    f"**{ReportText.EXTENDED_ABSENCE_JODIS}:** {due_cycles_display}\n"
                    f"**{ReportText.EXHAUSTED_JODIS}:** {exhausted_display}\n"
                )
                pdf.chapter_body(analysis_body)
            
            # Add Disclaimer
            pdf.set_y(-30)
            pdf.set_font('DejaVu', '', 8)
            pdf.set_text_color(128)
            pdf.multi_cell(0, 5, ReportText.DISCLAIMER_LONG, align='C')

            pdf.output(pdf_output_path)
            logging.info(f"📄 PDF Report saved to {pdf_output_path}")

    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)

if __name__ == "__main__":
    main()