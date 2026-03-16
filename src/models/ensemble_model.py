import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EnsembleModel:
    """
    Ensemble Model combining multiple quantitative models.
    final_score = 0.35 * heat_model + 0.25 * digit_model + 0.20 * gap_model + 0.20 * mirror_model
    """
    
    def __init__(self, models: dict, weights: dict):
        self.models = models
        self.weights = weights
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Combines predictions from multiple models.
        """
        if df.empty:
            return pd.DataFrame()
            
        combined_scores = pd.Series(0.0, index=self.all_jodis)
        
        for name, model in self.models.items():
            weight = self.weights.get(name, 0.0)
            if weight == 0:
                continue
                
            predictions = model.predict(df)
            if predictions.empty:
                continue
                
            # Normalize scores to [0, 1] for fair weight distribution
            if predictions['score'].max() > 0:
                predictions['score'] = predictions['score'] / predictions['score'].max()
            
            # Map predictions back to all jodis
            score_map = predictions.set_index('jodi')['score'].reindex(self.all_jodis, fill_value=0.0)
            combined_scores += score_map * weight
            
        final_predictions = pd.DataFrame({
            'jodi': combined_scores.index,
            'score': combined_scores.values
        })
        
        final_predictions = final_predictions.sort_values('score', ascending=False).reset_index(drop=True)
        final_predictions['rank'] = final_predictions.index + 1
        
        return final_predictions
