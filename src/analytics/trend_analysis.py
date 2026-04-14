import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TrendAnalyzer:
    """Analyzes market trends and momentum."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_market_momentum(self, short_window=7, long_window=30) -> str:
        """Determines if the market is 'Active', 'Stable', or 'Quiet' based on data volatility."""
        if len(self.df) < long_window:
            return "Stable"

        recent_count = len(self.df.tail(short_window))
        if recent_count < short_window:
            return "Quiet"

        # In a real scenario, this would analyze changes in winning patterns.
        # For simplicity, we characterize it by the frequency of repeats in the short window.
        repeats = self.df.tail(short_window)["jodi"].duplicated().sum()

        if repeats >= 2:
            return "Active (Pattern Repetition)"
        elif repeats == 1:
            return "Stable"
        else:
            return "Diversifying"

    def get_last_seen_summary(self) -> dict:
        """Returns how many days ago each jodi was last seen."""
        latest_date = self.df["date"].max()
        summary = {}
        for jodi in self.df["jodi"].unique():
            last_date = self.df[self.df["jodi"] == jodi]["date"].max()
            summary[jodi] = (latest_date - last_date).days
        return summary
