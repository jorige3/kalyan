import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DigitAnalyzer:
    """Analyzes frequencies and patterns of open and close digits."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_frequencies(self, window=30) -> dict:
        """Returns frequency of each digit in the specified window."""
        latest_df = self.df.tail(window)

        open_freq = (
            latest_df["open_digit"]
            .value_counts(normalize=True)
            .reindex(range(10), fill_value=0)
            .to_dict()
        )
        close_freq = (
            latest_df["close_digit"]
            .value_counts(normalize=True)
            .reindex(range(10), fill_value=0)
            .to_dict()
        )

        return {"open": open_freq, "close": close_freq}

    def get_hot_digits(self, top_n=3, window=30) -> dict:
        """Returns the most frequent digits in the specified window."""
        freqs = self.get_frequencies(window)

        hot_open = sorted(freqs["open"].items(), key=lambda x: x[1], reverse=True)[:top_n]
        hot_close = sorted(freqs["close"].items(), key=lambda x: x[1], reverse=True)[:top_n]

        return {
            "open": [digit for digit, freq in hot_open],
            "close": [digit for digit, freq in hot_close],
        }
