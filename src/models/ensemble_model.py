import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EnsembleModel:
    """
    Ensemble Model combining Heat, Matrix, Momentum, Markov v1, and Markov v2.
    final_score = weighted sum of normalized model scores.
    """

    def __init__(self, heat_model, matrix_model, momentum_model, markov_model=None, markov_v2_model=None, weights=None):
        self.models = {
            "heat": heat_model, 
            "matrix": matrix_model, 
            "momentum": momentum_model,
            "markov": markov_model,
            "markov_v2": markov_v2_model
        }
        self.weights = weights or {
            "heat": 0.25, 
            "matrix": 0.25, 
            "momentum": 0.15, 
            "markov": 0.10,
            "markov_v2": 0.25
        }
        self.all_jodis = [f"{i:02d}" for i in range(100)]

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Combines predictions from specialized models.
        """
        if df.empty:
            return pd.DataFrame()

        combined_scores = pd.Series(0.0, index=self.all_jodis)

        for name, model in self.models.items():
            if model is None:
                continue
                
            weight = self.weights.get(name, 0.0)
            if weight == 0:
                continue

            predictions = model.predict(df)
            if predictions.empty:
                logger.warning(f"Model {name} returned no predictions.")
                continue

            # Ensure jodi is string and 2 digits
            predictions["jodi"] = predictions["jodi"].astype(str).str.zfill(2)

            # Normalize scores to [0, 1] for fair weight distribution
            max_score = predictions["score"].max()
            min_score = predictions["score"].min()

            if max_score > min_score:
                norm_scores = (predictions["score"] - min_score) / (max_score - min_score)
            else:
                norm_scores = predictions["score"] / (max_score if max_score > 0 else 1.0)

            # Map predictions back to all jodis
            score_map = pd.Series(norm_scores.values, index=predictions["jodi"]).reindex(
                self.all_jodis, fill_value=0.0
            )
            combined_scores += score_map * weight

        final_predictions = pd.DataFrame(
            {"jodi": combined_scores.index, "score": combined_scores.values}
        )

        final_predictions = final_predictions.sort_values("score", ascending=False).reset_index(
            drop=True
        )
        final_predictions["rank"] = final_predictions.index + 1

        return final_predictions
