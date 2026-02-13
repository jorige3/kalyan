from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd


class HotColdAnalyzer:
    """
    Analyzes historical Kalyan data to identify hot (frequently occurring)
    and cold (infrequently occurring) digits and jodis.
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("DataFrame cannot be empty or None.")
        self.df = df.copy()
        self._validate_dataframe()

    def _validate_dataframe(self):
        """Ensures the DataFrame has the necessary columns."""
        required_cols = ['date', 'open', 'close', 'jodi']
        if not all(col in self.df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.dropna(subset=['open', 'close', 'jodi']) # Drop rows with missing key data

    def _get_recent_data(self, lookback_days: int) -> pd.DataFrame:
        """Filters data for a specified lookback period."""
        if self.df.empty:
            return pd.DataFrame()
        
        latest_date = self.df['date'].max()
        start_date = latest_date - timedelta(days=lookback_days)
        return self.df[self.df['date'] >= start_date]

    def get_digit_frequency(self, lookback_days: int = 30) -> pd.Series:
        """Calculates frequency of individual digits (0-9) in open and close over a lookback period."""
        recent_df = self._get_recent_data(lookback_days)
        if recent_df.empty:
            return pd.Series(dtype=int)

        open_freq = recent_df['open'].astype(int).value_counts().sort_index()
        close_freq = recent_df['close'].astype(int).value_counts().sort_index()
        
        # Combine frequencies, handling missing digits
        all_digits = pd.Series(range(10))
        combined_freq = pd.concat([open_freq, close_freq], axis=1).sum(axis=1).reindex(all_digits, fill_value=0)
        return combined_freq.sort_values(ascending=False)

    def get_jodi_frequency(self, lookback_days: int = 30) -> pd.Series:
        """Calculates frequency of Jodis over a lookback period."""
        recent_df = self._get_recent_data(lookback_days)
        if recent_df.empty:
            return pd.Series(dtype=int)
        
        return recent_df['jodi'].value_counts().sort_values(ascending=False)

    def get_hot_digits(self, lookback_days: int = 30, top_n: int = 5) -> Dict[str, int]:
        """Identifies the top N most frequent digits along with their frequencies."""
        freq = self.get_digit_frequency(lookback_days)
        return freq.head(top_n).rename(index=str).to_dict()

    def get_cold_digits(self, lookback_days: int = 30, bottom_n: int = 5) -> List[int]:
        """Identifies the bottom N least frequent digits."""
        freq = self.get_digit_frequency(lookback_days)
        return freq.tail(bottom_n).index.tolist()

    def get_hot_jodis(self, lookback_days: int = 30, top_n: int = 5) -> Dict[str, int]:
        """Identifies the top N most frequent jodis along with their frequencies."""
        freq = self.get_jodi_frequency(lookback_days)
        return freq.head(top_n).to_dict()

    def get_cold_jodis(self, lookback_days: int = 30, bottom_n: int = 5) -> List[str]:
        """Identifies the bottom N least frequent jodis."""
        freq = self.get_jodi_frequency(lookback_days)
        return freq.tail(bottom_n).index.tolist()

    def get_due_cycles(self, lookback_days: int = 90, threshold_days: int = 7) -> Dict[str, Dict[str, int]]:
        """
        Identifies jodis/digits that are 'due' based on their last appearance.
        A jodi/digit is due if it hasn't appeared for at least `threshold_days`
        within the `lookback_days` period. It now also returns the number of days overdue.
        """
        recent_df = self._get_recent_data(lookback_days)
        if recent_df.empty:
            return {"due_jodis": {}, "due_digits": {}}

        latest_date = recent_df['date'].max()

        # Due Jodis
        last_jodi_appearance = recent_df.groupby('jodi')['date'].max()
        due_jodis_with_days_overdue = {}
        for jodi, last_date in last_jodi_appearance.items():
            days_since_last_appearance = (latest_date - last_date).days
            if days_since_last_appearance >= threshold_days:
                due_jodis_with_days_overdue[jodi] = days_since_last_appearance

        # Due Digits (open and close)
        all_digits_data = pd.concat([
            recent_df[['date', 'open']].rename(columns={'open': 'digit'}),
            recent_df[['date', 'close']].rename(columns={'close': 'digit'})
        ])
        all_digits_data['digit'] = all_digits_data['digit'].astype(int)
        last_digit_appearance = all_digits_data.groupby('digit')['date'].max()
        due_digits_with_days_overdue = {}
        for digit, last_date in last_digit_appearance.items():
            days_since_last_appearance = (latest_date - last_date).days
            if days_since_last_appearance >= threshold_days:
                due_digits_with_days_overdue[str(digit)] = days_since_last_appearance
        
        return {"due_jodis": due_jodis_with_days_overdue, "due_digits": due_digits_with_days_overdue}

    def get_exhausted_numbers(self, lookback_days: int = 30, consecutive_hits: int = 3) -> Dict[str, Dict[str, int]]:
        """
        Identifies jodis/digits that might be 'exhausted' after a streak of consecutive hits.
        A jodi/digit is exhausted if it has appeared `consecutive_hits` or more times
        in the recent `lookback_days` period, along with their respective counts.
        """
        recent_df = self._get_recent_data(lookback_days)
        if recent_df.empty:
            return {"exhausted_jodis": {}, "exhausted_digits": {}}

        exhausted_jodis_with_counts = {}
        jodi_counts = recent_df['jodi'].value_counts()
        for jodi, count in jodi_counts.items():
            if count >= consecutive_hits:
                exhausted_jodis_with_counts[jodi] = count

        exhausted_digits_with_counts = {}
        digit_counts = self.get_digit_frequency(lookback_days)
        for digit, count in digit_counts.items():
            if count >= consecutive_hits: # Using the same threshold for digits
                exhausted_digits_with_counts[str(digit)] = count

        return {"exhausted_jodis": exhausted_jodis_with_counts, "exhausted_digits": exhausted_digits_with_counts}


if __name__ == '__main__':
    # Example Usage (requires a dummy DataFrame or actual data)
    # Create a dummy DataFrame for testing
    dates = [datetime.now() - timedelta(days=i) for i in range(60)]
    dummy_data = {
        'date': dates,
        'open': [i % 10 for i in range(60)],
        'close': [(i + 1) % 10 for i in range(60)],
        'jodi': [str(i % 10) + str((i + 1) % 10) for i in range(60)]
    }
    dummy_df = pd.DataFrame(dummy_data)
    
    # Add some specific patterns for testing exhausted/due
    dummy_df.loc[0:2, 'jodi'] = '11' # 3 consecutive '11'
    dummy_df.loc[50:55, 'open'] = 7 # 6 consecutive '7' open
    dummy_df.loc[50:55, 'close'] = 8 # 6 consecutive '8' close

    analyzer = HotColdAnalyzer(dummy_df)

    print("\nDigit Frequencies (last 30 days):")
    print(analyzer.get_digit_frequency(30))

    print("\nJodi Frequencies (last 30 days):")
    print(analyzer.get_jodi_frequency(30))

    print("\nHot Digits (last 30 days, top 3):")
    print(analyzer.get_hot_digits(30, 3))

    print("\nCold Digits (last 30 days, bottom 3):")
    print(analyzer.get_cold_digits(30, 3))

    print("\nHot Jodis (last 30 days, top 3):")
    print(analyzer.get_hot_jodis(30, 3))

    print("\nCold Jodis (last 30 days, bottom 3):")
    print(analyzer.get_cold_jodis(30, 3))

    print("\nDue Cycles (last 90 days, threshold 7 days):")
    print(analyzer.get_due_cycles(90, 7))

    print("\nExhausted Numbers (last 30 days, 3 consecutive hits):")
    print(analyzer.get_exhausted_numbers(30, 3))
