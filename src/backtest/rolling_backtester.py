import pandas as pd
from src.utils.logger import setup_logger
from datetime import timedelta

logger = setup_logger(__name__)

class RollingBacktester:
    """
    Rolling Backtester for prediction models.
    Evaluates model performance over historical data with no data leakage.
    """
    
    def __init__(self, model, start_date=None, window_days=365):
        self.model = model
        self.start_date = start_date
        self.window_days = window_days
        
    def run(self, df: pd.DataFrame) -> dict:
        """Runs the backtest and returns performance metrics."""
        if df.empty:
            return {}
            
        # Ensure date is datetime and jodi is string
        df['date'] = pd.to_datetime(df['date'])
        df['jodi'] = df['jodi'].astype(str).str.zfill(2)
        
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
            
            if predictions.empty:
                continue
                
            # Actual result for the test_date
            actual_jodi = df[df['date'] == test_date]['jodi'].values[0]
            
            # Check if actual jodi is in Top 5, Top 10, etc.
            top_5 = predictions.head(5)['jodi'].tolist()
            top_10 = predictions.head(10)['jodi'].tolist()
            
            # Find actual jodi's rank
            rank_series = predictions[predictions['jodi'] == actual_jodi]['rank']
            actual_rank = rank_series.values[0] if not rank_series.empty else 101
            
            results.append({
                'date': test_date,
                'actual': actual_jodi,
                'hit_top_5': actual_jodi in top_5,
                'hit_top_10': actual_jodi in top_10,
                'rank': actual_rank,
                'year': test_date.year
            })
            
        results_df = pd.DataFrame(results)
        
        if results_df.empty:
            return {}

        # Aggregate metrics
        hit_rate_top_5 = results_df['hit_top_5'].mean()
        hit_rate_top_10 = results_df['hit_top_10'].mean()
        
        # Yearly Breakdown
        yearly_breakdown = results_df.groupby('year').agg({
            'hit_top_5': 'mean',
            'hit_top_10': 'mean',
            'actual': 'count'
        }).rename(columns={'actual': 'total_days'}).to_dict('index')
        
        metrics = {
            'hit_rate_top_5': hit_rate_top_5,
            'hit_rate_top_10': hit_rate_top_10,
            'total_days': len(results_df),
            'avg_rank': results_df['rank'].mean(),
            'yearly_breakdown': yearly_breakdown
        }
        
        logger.info(f"Backtest complete. Total Days: {metrics['total_days']}, Top 5: {hit_rate_top_5:.2%}, Top 10: {hit_rate_top_10:.2%}")
        return metrics
