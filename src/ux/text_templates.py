# -*- coding: utf-8 -*-
"""
src/ux/text_templates.py

Centralized text templates for all user-facing output.
This allows for easy management of tone, wording, and localization.
"""

class ReportText:
    """
    Contains all static text for console and PDF reports.
    Using a class structure provides a clear namespace.
    """
    # --- General & Metadata ---
    PROJECT_TITLE = "Kalyan Market Analysis"
    VERSION = "2.1.0"
    REPORT_TYPE = "Daily Analysis Report"
    DATE_FORMAT = "%d-%b-%Y"
    
    # --- PDF & Console Headers ---
    PDF_HEADER_TITLE = "Kalyan Market Analysis"
    CONSOLE_HEADER_TITLE = "KALYAN MARKET ANALYSIS"
    
    # --- Section Titles ---
    SUMMARY_SECTION_TITLE = "Daily Market Summary"
    PICKS_SECTION_TITLE = "Highest Confidence Projections"
    DETAILED_ANALYSIS_SECTION_TITLE = "Detailed Analysis Breakdown"
    FREQUENCY_ANALYSIS_TITLE = "Frequency & Momentum"
    CYCLE_ANALYSIS_TITLE = "Cycles & Exhaustion"
    
    # --- Summary Content ---
    SUMMARY_MOOD = "Overall Market Mood"
    SUMMARY_STRONGEST_SIGNALS = "Strongest Signals Today"
    SUMMARY_CAUTION_AREAS = "Areas for Caution"
    SUMMARY_CONFIDENCE = "Analytical Confidence"
    
    # --- Analysis Labels ---
    HIGH_FREQUENCY_JODIS = "High-Frequency Jodis"
    HIGH_FREQUENCY_DIGITS = "High-Frequency Digits"
    EXTENDED_ABSENCE_JODIS = "Extended Absence Jodis (Due)"
    EXHAUSTED_JODIS = "Over-Represented Jodis (Exhausted)"
    
    # --- Confidence & Justification ---
    CONFIDENCE_HIGH = "High"
    CONFIDENCE_MEDIUM = "Medium"
    CONFIDENCE_LOW = "Low"
    
    # --- Disclaimers & Footers ---
    DISCLAIMER_SHORT = "For analytical and educational purposes only."
    DISCLAIMER_LONG = (
        "This report is a statistical analysis of historical data and does not constitute a "
        "prediction or guarantee of future results. All decisions based on this report are "
        "the sole responsibility of the user. Past performance is not an indicator of future results."
    )
    VERBOSE_MODE_HINT = "(Run with --verbose for full analytical breakdown)"

