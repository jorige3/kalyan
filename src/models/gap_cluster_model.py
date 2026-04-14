import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GapClusterModel:
    """
    Gap Cluster Model.
    Identifies jodis absent for 25-40 days.
    """

    def __init__(self, min_gap=25, max_gap=40):
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.all_jodis = [f"{i:02d}" for i in range(100)]

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates probability scores based on absence gaps.
        """
        if df.empty:
            return pd.DataFrame()

        latest_date = df["date"].max()
        scores = {}

        for jodi in self.all_jodis:
            last_seen = df[df["jodi"] == jodi]["date"].max()
            if pd.isna(last_seen):
                gap = 999
            else:
                gap = (latest_date - last_seen).days

            # Boost jodis in the specified gap cluster
            if self.min_gap <= gap <= self.max_gap:
                # Closer to the center of the gap cluster gets higher score
                center = (self.min_gap + self.max_gap) / 2.0
                dist = abs(gap - center)
                scores[jodi] = 1.0 - (dist / (self.max_gap - self.min_gap))
            else:
                scores[jodi] = 0.0

        predictions = pd.DataFrame({"jodi": list(scores.keys()), "score": list(scores.values())})

        predictions = predictions.sort_values("score", ascending=False).reset_index(drop=True)
        predictions["rank"] = predictions.index + 1

        return predictions
