import pandas as pd
from src.analytics.jodi_matrix import compute_jodi_matrix
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MatrixModel:
    """
    MatrixModel: Uses a probabilistic matrix based on digit distributions 
    and conditional panel data relationship.
    """
    
    def __init__(self, window=60):
        self.window = window
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        
    def fit(self, df: pd.DataFrame):
        """Standard model interface for fitting (if needed)."""
        pass
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates 00-99 matrix predictions.
        Compatible with Ensemble and Backtester.
        """
        if df.empty:
            return pd.DataFrame()
            
        ranked_scores = compute_jodi_matrix(df, last_n_days=self.window)
        
        if not ranked_scores:
            return pd.DataFrame()
            
        predictions = pd.DataFrame(ranked_scores, columns=['jodi', 'score'])
        predictions['rank'] = range(1, 101)
        
        return predictions

    def predict_top_n(self, df: pd.DataFrame, n=10) -> pd.DataFrame:
        """Returns the top N predictions."""
        predictions = self.predict(df)
        return predictions.head(n)
