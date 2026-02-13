# -*- coding: utf-8 -*-
"""
src/analysis/sangam_analysis.py

Module for advanced Sangam analysis, including hot, cold, and due Sangams.
"""

from typing import Dict

import pandas as pd


class SangamAnalyzer:
    """
    Analyzes Sangam patterns, including identifying hot, cold, and due Sangams.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Ensure 'open_sangam' and 'close_sangam' columns exist
        if 'open_sangam' not in self.df.columns or 'close_sangam' not in self.df.columns:
            raise ValueError("DataFrame must contain 'open_sangam' and 'close_sangam' columns for Sangam analysis.")
        
        # Ensure sangam columns are string type
        self.df['open_sangam'] = self.df['open_sangam'].astype(str)
        self.df['close_sangam'] = self.df['close_sangam'].astype(str)

    def get_hot_sangams(self, lookback_days: int = 30, top_n: int = 5) -> Dict[str, Dict[str, int]]:
        """
        Identifies 'hot' open and close Sangams based on their frequency in recent days,
        along with their respective frequency counts.
        """
        latest_date = self.df['date'].max()
        recent_df = self.df[self.df['date'] >= (latest_date - pd.Timedelta(days=lookback_days))]

        hot_open_sangams = recent_df['open_sangam'].value_counts().head(top_n).to_dict()
        hot_close_sangams = recent_df['close_sangam'].value_counts().head(top_n).to_dict()

        return {
            "hot_open_sangams": hot_open_sangams,
            "hot_close_sangams": hot_close_sangams
        }

    def get_due_sangams(self, lookback_days: int = 60) -> Dict[str, Dict[str, int]]:
        """
        Identifies 'due' open and close Sangams based on their absence in recent days,
        along with the number of days they are overdue.
        """
        latest_date = self.df['date'].max()
        recent_df = self.df[self.df['date'] >= (latest_date - pd.Timedelta(days=lookback_days))]

        # Due Open Sangams
        last_open_sangam_appearance = self.df.groupby('open_sangam')['date'].max()
        due_open_sangams_with_days_overdue = {}
        for sangam, last_date in last_open_sangam_appearance.items():
            # A sangam is considered "due" if it hasn't appeared in the recent_df
            # and we calculate how many days it has been since its last appearance in the full historical data
            if sangam not in recent_df['open_sangam'].values:
                days_since_last_appearance = (latest_date - last_date).days
                due_open_sangams_with_days_overdue[sangam] = days_since_last_appearance
        
        # Due Close Sangams
        last_close_sangam_appearance = self.df.groupby('close_sangam')['date'].max()
        due_close_sangams_with_days_overdue = {}
        for sangam, last_date in last_close_sangam_appearance.items():
            if sangam not in recent_df['close_sangam'].values:
                days_since_last_appearance = (latest_date - last_date).days
                due_close_sangams_with_days_overdue[sangam] = days_since_last_appearance
        
        return {
            "due_open_sangams": due_open_sangams_with_days_overdue,
            "due_close_sangams": due_close_sangams_with_days_overdue
        }

    # Placeholder for other advanced Sangam analysis methods
    def get_sangam_cycle_streaks(self) -> Dict:
        """
        Identifies streaks or cycles in Sangam appearances. (Placeholder)
        """
        return {"open_sangam_streaks": [], "close_sangam_streaks": []}

    def get_sangam_digit_dominance(self) -> Dict:
        """
        Analyzes the dominance of individual digits within Sangams. (Placeholder)
        """
        return {"open_sangam_digit_dominance": {}, "close_sangam_digit_dominance": {}}
