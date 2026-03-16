import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MomentumModel:
    """
    Momentum Model for Jodi predictions.
    Focuses on jodis that have appeared recently.
    """
    
    def __init__(self, window=7):
        self.window = window
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates predictions based on recent momentum.
        """
        if df.empty:
            return pd.DataFrame()
            
        latest_date = df['date'].max()
        recent_df = df[df['date'] > latest_date - pd.Timedelta(days=self.window)]
        
        # Simple frequency in the short window
        counts = recent_df['jodi'].value_counts(normalize=True).reindex(self.all_jodis, fill_value=0)
        
        predictions = pd.DataFrame({
            'jodi': counts.index,
            'score': counts.values
        })
        
        predictions = predictions.sort_values('score', ascending=False).reset_index(drop=True)
        predictions['rank'] = predictions.index + 1
        
        return predictions
