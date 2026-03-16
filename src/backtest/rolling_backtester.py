import pandas as pd
from src.utils.logger import setup_logger
from datetime import timedelta

logger = setup_logger(__name__)

class RollingBacktester:
    """
    Rolling Backtester for prediction models.
    Evaluates model performance over historical data.
    """
    
    def __init__(self, model, start_date=None, window_days=365):
        self.model = model
        self.start_date = start_date
        self.window_days = window_days
        
    def run(self, df: pd.DataFrame) -> dict:
        """Runs the backtest and returns performance metrics."""
        if df.empty:
            return {}
            
        dates = sorted(df['date'].unique())
        if self.start_date:
            dates = [d for d in dates if d >= pd.to_datetime(self.start_date)]
        else:
            # Default to testing the last year of data
            self.start_date = dates[-self.window_days] if len(dates) > self.window_days else dates[0]
            dates = [d for d in dates if d >= self.start_date]
            
        results = []
        for i in range(len(dates) - 1):
            train_date = dates[i]
            test_date = dates[i+1]
            
            # Training data is everything up to the train_date (no leakage)
            train_df = df[df['date'] <= train_date]
            
            # Predict for the next day (test_date)
            predictions = self.model.predict(train_df)
            
            # Actual result for the test_date
            actual_jodi = df[df['date'] == test_date]['jodi'].values[0]
            
            # Check if actual jodi is in Top 5, Top 10, etc.
            top_5 = predictions.head(5)['jodi'].tolist()
            top_10 = predictions.head(10)['jodi'].tolist()
            
            results.append({
                'date': test_date,
                'actual': actual_jodi,
                'hit_top_5': actual_jodi in top_5,
                'hit_top_10': actual_jodi in top_10,
                'rank': predictions[predictions['jodi'] == actual_jodi]['rank'].values[0]
            })
            
        results_df = pd.DataFrame(results)
        
        hit_rate_top_5 = results_df['hit_top_5'].mean()
        hit_rate_top_10 = results_df['hit_top_10'].mean()
        
        metrics = {
            'hit_rate_top_5': hit_rate_top_5,
            'hit_rate_top_10': hit_rate_top_10,
            'total_days': len(results_df),
            'avg_rank': results_df['rank'].mean()
        }
        
        logger.info(f"Backtest complete. Hit Rate Top 5: {hit_rate_top_5:.2%}, Top 10: {hit_rate_top_10:.2%}")
        return metrics
