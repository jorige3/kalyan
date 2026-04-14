import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MirrorPairModel:
    """
    Mirror Pair Model.
    Boosts jodi 'YX' if 'XY' appeared recently (e.g., last 7 days).
    """

    def __init__(self, window=7):
        self.window = window
        self.all_jodis = [f"{i:02d}" for i in range(100)]

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Boosts mirror pairs based on recent data.
        """
        if df.empty:
            return pd.DataFrame()

        latest_date = df["date"].max()
        recent_df = df[df["date"] > latest_date - pd.Timedelta(days=self.window)]
        recent_jodis = recent_df["jodi"].unique()

        scores = {}
        for jodi in self.all_jodis:
            # Mirror of 'XY' is 'YX'
            mirror = jodi[::-1]
            if mirror in recent_jodis:
                # Mirror has appeared recently, boost this jodi
                scores[jodi] = 1.0
            else:
                scores[jodi] = 0.0

        predictions = pd.DataFrame({"jodi": list(scores.keys()), "score": list(scores.values())})

        predictions = predictions.sort_values("score", ascending=False).reset_index(drop=True)
        predictions["rank"] = predictions.index + 1

        return predictions
