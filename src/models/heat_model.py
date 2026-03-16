import pandas as pd
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class HeatModel:
    """
    Heat Score Model for Jodi predictions.
    score = (recent_frequency * 0.7) + (absence_score * 0.2) + (long_term_frequency * 0.1)
    """
    
    def __init__(self, recent_window=30, long_term_window=180):
        self.recent_window = recent_window
        self.long_term_window = long_term_window
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates predictions based on historical data.
        Returns a DataFrame with jodi, score, and rank.
        """
        if df.empty:
            return pd.DataFrame()
            
        latest_date = df['date'].max()
        
        # Recent Frequency
        recent_df = df[df['date'] > latest_date - pd.Timedelta(days=self.recent_window)]
        recent_freq = recent_df['jodi'].value_counts(normalize=True).reindex(self.all_jodis, fill_value=0)
        
        # Long Term Frequency
        long_term_df = df[df['date'] > latest_date - pd.Timedelta(days=self.long_term_window)]
        long_term_freq = long_term_df['jodi'].value_counts(normalize=True).reindex(self.all_jodis, fill_value=0)
        
        # Absence Score (Days since last appearance)
        absence_days = {}
        for jodi in self.all_jodis:
            last_seen = df[df['jodi'] == jodi]['date'].max()
            if pd.isna(last_seen):
                # Never seen, give it a high absence score (e.g., long_term_window)
                days = self.long_term_window
            else:
                days = (latest_date - last_seen).days
            absence_days[jodi] = days
            
        absence_series = pd.Series(absence_days)
        # Normalize absence score to [0, 1]
        if absence_series.max() > 0:
            absence_score = absence_series / absence_series.max()
        else:
            absence_score = absence_series
            
        # Calculate Final Score
        final_scores = (recent_freq * 0.7) + (absence_score * 0.2) + (long_term_freq * 0.1)
        
        predictions = pd.DataFrame({
            'jodi': final_scores.index,
            'score': final_scores.values,
            'recent_freq': recent_freq.values,
            'absence_days': absence_series.values,
            'long_term_freq': long_term_freq.values
        })
        
        predictions = predictions.sort_values('score', ascending=False).reset_index(drop=True)
        predictions['rank'] = predictions.index + 1
        
        return predictions
