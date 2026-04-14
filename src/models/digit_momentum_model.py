import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DigitMomentumModel:
    """
    Digit Momentum Model.
    Scores jodi pairs based on the frequency of their constituent digits in a recent window.
    """

    def __init__(self, window=30):
        self.window = window
        self.all_jodis = [f"{i:02d}" for i in range(100)]

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates scores based on digit momentum.
        """
        if df.empty:
            return pd.DataFrame()

        latest_date = df["date"].max()
        recent_df = df[df["date"] > latest_date - pd.Timedelta(days=self.window)]

        # Calculate digit frequencies
        open_digits = (
            recent_df["open_digit"].value_counts(normalize=True).reindex(range(10), fill_value=0)
        )
        close_digits = (
            recent_df["close_digit"].value_counts(normalize=True).reindex(range(10), fill_value=0)
        )

        scores = {}
        for jodi in self.all_jodis:
            d1, d2 = int(jodi[0]), int(jodi[1])
            # Score is the average strength of both digits
            scores[jodi] = (open_digits[d1] + close_digits[d2]) / 2.0

        predictions = pd.DataFrame({"jodi": list(scores.keys()), "score": list(scores.values())})

        # Normalize score to [0, 1]
        if predictions["score"].max() > 0:
            predictions["score"] = predictions["score"] / predictions["score"].max()

        predictions = predictions.sort_values("score", ascending=False).reset_index(drop=True)
        predictions["rank"] = predictions.index + 1

        return predictions
