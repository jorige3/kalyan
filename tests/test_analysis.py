from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

from main import generate_daily_summary_and_confidence  # Import the function for testing
from src.analysis.hot_cold import HotColdAnalyzer
from src.analysis.sangam_analysis import SangamAnalyzer
from src.analysis.trend_window import TrendWindowAnalyzer


@pytest.fixture
def dummy_dataframe_for_analysis():
    """
    Provides a dummy DataFrame for testing analysis modules.
    Includes jodis and sangams for comprehensive testing.
    """
    dates = [datetime.now() - timedelta(days=i) for i in range(100, 0, -1)] # 100 days data, ascending date
    data = []
    for i, d in enumerate(dates):
        open_digit = i % 10
        close_digit = (i + 1) % 10
        jodi = f"{open_digit}{close_digit}"
        
        # Simple dummy sangams for testing purposes
        open_sangam = f"{open_digit}{i % 10}{ (i + 2) % 10}"
        close_sangam = f"{close_digit}{(i + 3) % 10}{(i + 4) % 10}"

        data.append({
            "date": d,
            "open": open_digit,
            "close": close_digit,
            "jodi": jodi,
            "open_sangam": open_sangam,
            "close_sangam": close_sangam
        })
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# --- Tests for HotColdAnalyzer ---

def test_hot_cold_analyzer_init(dummy_dataframe_for_analysis):
    analyzer = HotColdAnalyzer(dummy_dataframe_for_analysis)
    assert not analyzer.df.empty

def test_hot_cold_analyzer_get_hot_jodis(dummy_dataframe_for_analysis):
    analyzer = HotColdAnalyzer(dummy_dataframe_for_analysis)
    hot_jodis = analyzer.get_hot_jodis(lookback_days=30, top_n=3)
    assert isinstance(hot_jodis, dict)
    assert len(hot_jodis) <= 3
    for jodi, freq in hot_jodis.items():
        assert isinstance(jodi, str)
        assert isinstance(freq, int)
        assert freq > 0

def test_hot_cold_analyzer_get_due_cycles(dummy_dataframe_for_analysis):
    # Manipulate data to create a "due" jodi
    test_df = dummy_dataframe_for_analysis.copy()
    test_df.loc[test_df['jodi'] == '01', 'date'] = datetime.now() - timedelta(days=10) # Make '01' due
    analyzer = HotColdAnalyzer(test_df)
    due_cycles = analyzer.get_due_cycles(lookback_days=30, threshold_days=7)
    assert isinstance(due_cycles, dict)
    assert 'due_jodis' in due_cycles
    assert 'due_digits' in due_cycles
    assert isinstance(due_cycles['due_jodis'], dict)
    assert isinstance(due_cycles['due_digits'], dict)
    # Check if '01' is in due_jodis and its days overdue is correct (or close)
    if '01' in due_cycles['due_jodis']:
        assert due_cycles['due_jodis']['01'] >= 7

def test_hot_cold_analyzer_get_exhausted_numbers(dummy_dataframe_for_analysis):
    # Manipulate data to create an "exhausted" jodi
    test_df = dummy_dataframe_for_analysis.copy()
    # Make '23' appear 5 times in the last few days
    for i in range(5):
        test_df.loc[len(test_df) - 1 - i, 'jodi'] = '23'
    analyzer = HotColdAnalyzer(test_df)
    exhausted = analyzer.get_exhausted_numbers(lookback_days=10, consecutive_hits=3)
    assert isinstance(exhausted, dict)
    assert 'exhausted_jodis' in exhausted
    assert 'exhausted_digits' in exhausted
    assert isinstance(exhausted['exhausted_jodis'], dict)
    assert isinstance(exhausted['exhausted_digits'], dict)
    if '23' in exhausted['exhausted_jodis']:
        assert exhausted['exhausted_jodis']['23'] >= 3

# --- Tests for TrendWindowAnalyzer ---

def test_trend_window_analyzer_init(dummy_dataframe_for_analysis):
    analyzer = TrendWindowAnalyzer(dummy_dataframe_for_analysis)
    assert not analyzer.df.empty

def test_trend_window_analyzer_get_due_cycles_by_last_appearance(dummy_dataframe_for_analysis):
    # Manipulate data to create a "due" jodi for trend window
    test_df = dummy_dataframe_for_analysis.copy()
    test_df.loc[test_df['jodi'] == '02', 'date'] = datetime.now() - timedelta(days=15) # Make '02' due
    analyzer = TrendWindowAnalyzer(test_df)
    due_cycles = analyzer.get_due_cycles_by_last_appearance(lookback_days=30, threshold_days=7)
    assert isinstance(due_cycles, dict)
    assert 'due_jodis' in due_cycles
    assert 'due_digits' in due_cycles
    assert isinstance(due_cycles['due_jodis'], dict)
    assert isinstance(due_cycles['due_digits'], dict)
    if '02' in due_cycles['due_jodis']:
        assert due_cycles['due_jodis']['02'] >= 7

def test_trend_window_analyzer_get_exhausted_numbers_by_streak(dummy_dataframe_for_analysis):
    # Manipulate data to create an "exhausted" jodi for trend window
    test_df = dummy_dataframe_for_analysis.copy()
    for i in range(4):
        test_df.loc[len(test_df) - 1 - i, 'jodi'] = '34'
    analyzer = TrendWindowAnalyzer(test_df)
    exhausted = analyzer.get_exhausted_numbers_by_streak(lookback_days=10, consecutive_hits=3)
    assert isinstance(exhausted, dict)
    assert 'exhausted_jodis' in exhausted
    assert 'exhausted_digits' in exhausted
    assert isinstance(exhausted['exhausted_jodis'], dict)
    assert isinstance(exhausted['exhausted_digits'], dict)
    if '34' in exhausted['exhausted_jodis']:
        assert exhausted['exhausted_jodis']['34'] >= 3

# --- Tests for SangamAnalyzer ---

def test_sangam_analyzer_init(dummy_dataframe_for_analysis):
    analyzer = SangamAnalyzer(dummy_dataframe_for_analysis)
    assert not analyzer.df.empty

def test_sangam_analyzer_get_hot_sangams(dummy_dataframe_for_analysis):
    analyzer = SangamAnalyzer(dummy_dataframe_for_analysis)
    hot_sangams = analyzer.get_hot_sangams(lookback_days=30, top_n=3)
    assert isinstance(hot_sangams, dict)
    assert 'hot_open_sangams' in hot_sangams
    assert 'hot_close_sangams' in hot_sangams
    assert isinstance(hot_sangams['hot_open_sangams'], dict)
    assert isinstance(hot_sangams['hot_close_sangams'], dict)
    assert len(hot_sangams['hot_open_sangams']) <= 3

def test_sangam_analyzer_get_due_sangams(dummy_dataframe_for_analysis):
    # Manipulate data to create a "due" open sangam
    test_df = dummy_dataframe_for_analysis.copy()
    test_df.loc[test_df['open_sangam'] == '002', 'date'] = datetime.now() - timedelta(days=70) # Make '002' due
    analyzer = SangamAnalyzer(test_df)
    due_sangams = analyzer.get_due_sangams(lookback_days=60) # top_n is no longer used
    assert isinstance(due_sangams, dict)
    assert 'due_open_sangams' in due_sangams
    assert 'due_close_sangams' in due_sangams
    assert isinstance(due_sangams['due_open_sangams'], dict)
    assert isinstance(due_sangams['due_close_sangams'], dict)
    if '002' in due_sangams['due_open_sangams']:
        assert due_sangams['due_open_sangams']['002'] >= 60

# --- Tests for generate_daily_summary_and_confidence in main.py ---

# This requires mocking config.SCORING_WEIGHTS



@pytest.fixture

def mock_config_weights():

    with patch('config.SCORING_WEIGHTS', {
        "HIGH_FREQUENCY_JODI": 1.0,
        "TREND_ALIGNED_JODI": 1.0,
        "EXTENDED_ABSENCE_JODI": 1.0,
        "EXHAUSTED_PATTERN_PENALTY": -1.0,
        "HIGH_FREQUENCY_OPEN_SANGAM": 1.0,
        "HIGH_FREQUENCY_CLOSE_SANGAM": 1.0,
        "EXTENDED_ABSENCE_OPEN_SANGAM": 1.0,
        "EXTENDED_ABSENCE_CLOSE_SANGAM": 1.0,
    }):
        yield

def test_generate_daily_summary_and_confidence_scoring(mock_config_weights):
    # Create dummy analysis results matching the new dictionary structure
    analysis_results = {
        "hot_jodis": {"12": 5, "34": 3},
        "due_jodis": {}, # Placeholder
        "trend_due_jodis": {}, # Placeholder
        "exhausted_jodis": {"34": 4},
        "hot_open_sangams": {}, # Placeholder
        "hot_close_sangams": {}, # Placeholder
        "due_open_sangams": {}, # Placeholder
        "due_close_sangams": {}, # Placeholder
    }

    summary = generate_daily_summary_and_confidence(analysis_results)
    assert 'top_picks_with_confidence' in summary
    assert isinstance(summary['top_picks_with_confidence'], list)
    assert len(summary['top_picks_with_confidence']) == 2 # Expecting only 2 picks

    # Verify a pick that should have a high score
    # "12" is hot_jodi (5) = 5*1 = 5.0
    found_12 = False
    for pick in summary['top_picks_with_confidence']:
        if pick['value'] == '12':
            assert pick['score'] == 5.0
            assert pick['confidence'] == 'High' # assuming default thresholds (5.0 > 2.5)
            found_12 = True
            break
    assert found_12, "Pick '12' not found or scored incorrectly"

    # Verify a pick with a penalty
    # "34" is hot_jodi (3) and exhausted (4) = 3*1 - 4*1 = -1.0
    found_34 = False
    for pick in summary['top_picks_with_confidence']:
        if pick['value'] == '34':
            assert pick['score'] == -1.0
            assert pick['confidence'] == 'Low' # assuming default thresholds (-1.0 < 1.0)
            found_34 = True
            break
    assert found_34, "Pick '34' not found or scored incorrectly"

