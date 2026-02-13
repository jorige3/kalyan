from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd


class TrendWindowAnalyzer:
    """
    Analyzes historical Kalyan data using a sliding window approach to identify
    trends and cycles for digits and jodis.
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("DataFrame cannot be empty or None.")
        self.df = df.copy()
        self._validate_dataframe()

    def _validate_dataframe(self):
        """Ensures the DataFrame has the necessary columns and correct types."""
        required_cols = ['date', 'open', 'close', 'jodi']
        if not all(col in self.df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values(by='date').reset_index(drop=True)
        self.df = self.df.dropna(subset=['open', 'close', 'jodi']) # Drop rows with missing key data

    def _get_window_data(self, end_date: datetime, window_size: int) -> pd.DataFrame:
        """
        Retrieves data for a specific window ending on `end_date` with `window_size` days.
        """
        start_date = end_date - timedelta(days=window_size - 1)
        return self.df[(self.df['date'] >= start_date) & (self.df['date'] <= end_date)]

    def get_jodi_cycle_gaps(self, jodi: str) -> List[int]:
        """
        Calculates the number of days between occurrences of a specific jodi.
        Returns a list of gap lengths.
        """
        jodi_dates = self.df[self.df['jodi'] == jodi]['date'].tolist()
        if len(jodi_dates) < 2:
            return []
        
        gaps = []
        for i in range(1, len(jodi_dates)):
            gap = (jodi_dates[i] - jodi_dates[i-1]).days
            gaps.append(gap)
        return gaps

    def get_digit_cycle_gaps(self, digit: int, column: str = 'open') -> List[int]:
        """
        Calculates the number of days between occurrences of a specific digit
        in a given column ('open' or 'close').
        Returns a list of gap lengths.
        """
        if column not in ['open', 'close']:
            raise ValueError("Column must be 'open' or 'close'.")
        
        digit_dates = self.df[self.df[column].astype(int) == digit]['date'].tolist()
        if len(digit_dates) < 2:
            return []
        
        gaps = []
        for i in range(1, len(digit_dates)):
            gap = (digit_dates[i] - digit_dates[i-1]).days
            gaps.append(gap)
        return gaps

    def analyze_jodi_trends_in_window(self, end_date: datetime, window_size: int = 30) -> Dict[str, int]:
        """
        Analyzes the frequency of each jodi within a sliding window.
        Returns a dictionary with jodi as key and its count as value.
        """
        window_df = self._get_window_data(end_date, window_size)
        if window_df.empty:
            return {}
        return window_df['jodi'].value_counts().to_dict()

    def analyze_digit_trends_in_window(self, end_date: datetime, window_size: int = 30) -> Dict[int, int]:
        """
        Analyzes the frequency of each digit (open and close combined) within a sliding window.
        Returns a dictionary with digit as key and its count as value.
        """
        window_df = self._get_window_data(end_date, window_size)
        if window_df.empty:
            return {}
        
        open_digits = window_df['open'].dropna().astype(int)
        close_digits = window_df['close'].dropna().astype(int)
        
        all_digits = pd.concat([open_digits, close_digits])
        return all_digits.value_counts().to_dict()

    def get_due_cycles_by_last_appearance(self, lookback_days: int = 90, threshold_days: int = 7) -> Dict[str, Dict[str, int]]:
        """
        Identifies jodis/digits that are 'due' based on their last appearance within a lookback period.
        A jodi/digit is due if it hasn't appeared for at least `threshold_days`,
        along with their respective days overdue.
        """
        if self.df.empty:
            return {"due_jodis": {}, "due_digits": {}}

        latest_date = self.df['date'].max()
        start_date = latest_date - timedelta(days=lookback_days)
        recent_df = self.df[self.df['date'] >= start_date]

        if recent_df.empty:
            return {"due_jodis": {}, "due_digits": {}}

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

    def get_exhausted_numbers_by_streak(self, lookback_days: int = 30, consecutive_hits: int = 3) -> Dict[str, Dict[str, int]]:
        """
        Identifies jodis/digits that might be 'exhausted' after a streak of consecutive hits
        within a lookback period, along with their respective counts.
        """
        if self.df.empty:
            return {"exhausted_jodis": {}, "exhausted_digits": {}}

        latest_date = self.df['date'].max()
        start_date = latest_date - timedelta(days=lookback_days)
        recent_df = self.df[self.df['date'] >= start_date]

        if recent_df.empty:
            return {"exhausted_jodis": {}, "exhausted_digits": {}}

        exhausted_jodis_with_counts = {}
        jodi_counts = recent_df['jodi'].value_counts()
        for jodi, count in jodi_counts.items():
            if count >= consecutive_hits:
                exhausted_jodis_with_counts[jodi] = count

        exhausted_digits_with_counts = {}
        # Combine open and close digits for frequency analysis
        all_digits = pd.concat([recent_df['open'].dropna().astype(int), recent_df['close'].dropna().astype(int)])
        digit_counts = all_digits.value_counts()
        for digit, count in digit_counts.items():
            if count >= consecutive_hits:
                exhausted_digits_with_counts[str(digit)] = count

        return {"exhausted_jodis": exhausted_jodis_with_counts, "exhausted_digits": exhausted_digits_with_counts}


if __name__ == '__main__':
    # Example Usage (requires a dummy DataFrame or actual data)
    # Create a dummy DataFrame for testing
    dates = [datetime.now() - timedelta(days=i) for i in range(100)]
    dummy_data = {
        'date': dates,
        'open': [i % 10 for i in range(100)],
        'close': [(i + 1) % 10 for i in range(100)],
        'jodi': [str(i % 10) + str((i + 1) % 10) for i in range(100)]
    }
    dummy_df = pd.DataFrame(dummy_data)
    
    # Add some specific patterns for testing exhausted/due
    dummy_df.loc[0:2, 'jodi'] = '11' # 3 consecutive '11'
    dummy_df.loc[50:55, 'open'] = 7 # 6 consecutive '7' open
    dummy_df.loc[50:55, 'close'] = 8 # 6 consecutive '8' close

    analyzer = TrendWindowAnalyzer(dummy_df)

    latest_date = dummy_df['date'].max()

    print(f"\nJodi Trends in 30-day window ending {latest_date.date()}:")
    print(analyzer.analyze_jodi_trends_in_window(latest_date, 30))

    print(f"\nDigit Trends in 30-day window ending {latest_date.date()}:")
    print(analyzer.analyze_digit_trends_in_window(latest_date, 30))

    print("\nJodi Cycle Gaps for '11':")
    print(analyzer.get_jodi_cycle_gaps('11'))

    print("\nDigit Cycle Gaps for '7' (open):")
    print(analyzer.get_digit_cycle_gaps(7, 'open'))

    print("\nDue Cycles (last 90 days, threshold 7 days):")
    print(analyzer.get_due_cycles_by_last_appearance(90, 7))

    print("\nExhausted Numbers (last 30 days, 3 consecutive hits):")
    print(analyzer.get_exhausted_numbers_by_streak(30, 3))
