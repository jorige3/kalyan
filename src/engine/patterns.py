from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


class Patterns:
    """
    Analyzes various patterns in Kalyan Matka data including digit sums, mirror numbers,
    weekday biases, and jodi separation.
    """

    def __init__(self, kalyan_engine):
        self.kalyan_engine = kalyan_engine
        self.df = self.kalyan_engine.get_historical_data()

    def _calculate_digit_sum(self, number_str: str) -> int:
        """Calculates the single-digit sum of a number string."""
        number_str = str(number_str) # Ensure it's a string
        if not number_str or not number_str.isdigit():
            return -1 # Invalid input
        total = sum(int(digit) for digit in number_str)
        return total % 10 if total >= 10 else total

    def _get_mirror_jodi(self, jodi_str: str) -> str:
        """Returns the mirror jodi for a given jodi string."""
        if len(jodi_str) != 2 or not jodi_str.isdigit():
            return "" # Invalid input
        open_digit = int(jodi_str[0])
        close_digit = int(jodi_str[1])
        mirror_open = (open_digit + 5) % 10 if open_digit < 5 else (open_digit - 5) % 10
        mirror_close = (close_digit + 5) % 10 if close_digit < 5 else (close_digit - 5) % 10
        return f"{mirror_open}{mirror_close}"

    def get_digit_sum_patterns(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Analyzes digit sum patterns for open, close, and jodi.
        Returns frequencies of digit sums.
        """
        recent_data = self.df.tail(lookback_days)
        
        open_sum_freq = recent_data['open'].apply(self._calculate_digit_sum).value_counts().to_dict()
        close_sum_freq = recent_data['close'].apply(self._calculate_digit_sum).value_counts().to_dict()
        jodi_sum_freq = recent_data['jodi'].apply(self._calculate_digit_sum).value_counts().to_dict()

        return {
            "open_sum_freq": open_sum_freq,
            "close_sum_freq": close_sum_freq,
            "jodi_sum_freq": jodi_sum_freq
        }

    def get_mirror_jodi_patterns(self, lookback_days: int = 30) -> List[str]:
        """
        Identifies recently played mirror jodis and their corresponding mirrors.
        Returns a list of mirror jodis that recently appeared.
        """
        recent_data = self.df.tail(lookback_days)
        played_jodis = recent_data['jodi'].dropna().unique().tolist()
        mirror_jodis_found = []
        for jodi in played_jodis:
            mirror = self._get_mirror_jodi(jodi)
            if mirror in played_jodis and jodi != mirror: # Avoid self-mirroring if logic allows
                mirror_jodis_found.append(jodi)
        return list(set(mirror_jodis_found)) # Return unique mirror jodis

    def get_weekday_biases(self, lookback_days: int = 90) -> Dict[str, Any]:
        """
        Analyzes biases for open/close digits and jodis based on the day of the week.
        Returns frequencies of digits/jodis per weekday.
        """
        recent_data = self.df.tail(lookback_days).copy()
        recent_data['weekday'] = recent_data['date'].dt.day_name()
        
        weekday_biases = {}
        for day in recent_data['weekday'].unique():
            day_data = recent_data[recent_data['weekday'] == day]
            weekday_biases[day] = {
                "open_digit_freq": day_data['open'].value_counts().to_dict(),
                "close_digit_freq": day_data['close'].value_counts().to_dict(),
                "jodi_freq": day_data['jodi'].value_counts().to_dict()
            }
        return weekday_biases

    def get_open_close_jodi_separation(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Analyzes the separation (difference) between open and close digits in jodis.
        Returns frequency of separation values.
        """
        recent_data = self.df.tail(lookback_days).copy()
        recent_data['open_int'] = recent_data['open'].apply(lambda x: int(x) if str(x).isdigit() else -1)
        recent_data['close_int'] = recent_data['close'].apply(lambda x: int(x) if str(x).isdigit() else -1)
        
        # Filter out invalid entries where conversion failed
        valid_data = recent_data[(recent_data['open_int'] != -1) & (recent_data['close_int'] != -1)]
        
        valid_data['jodi_separation'] = abs(valid_data['open_int'] - valid_data['close_int'])
        separation_freq = valid_data['jodi_separation'].value_counts().to_dict()
        return {"separation_freq": separation_freq}

    def get_hot_cold_streak_detection(self, lookback_days: int = 30, threshold: int = 5) -> Dict[str, Any]:
        """
        Detects hot (frequently appearing) and cold (rarely appearing) digits/jodis
        and identifies streaks.
        """
        recent_data = self.df.tail(lookback_days)
        
        # Hot/Cold Digits
        open_digit_freq = recent_data['open'].value_counts(normalize=True)
        close_digit_freq = recent_data['close'].value_counts(normalize=True)

        hot_digits = {
            'open': [d for d, freq in open_digit_freq.items() if freq > open_digit_freq.mean() and str(d).isdigit()],
            'close': [d for d, freq in close_digit_freq.items() if freq > close_digit_freq.mean() and str(d).isdigit()]
        }
        cold_digits = {
            'open': [d for d, freq in open_digit_freq.items() if freq < open_digit_freq.mean() and str(d).isdigit()],
            'close': [d for d, freq in close_digit_freq.items() if freq < close_digit_freq.mean() and str(d).isdigit()]
        }
        
        # Hot/Cold Jodis
        all_jodis = self.kalyan_engine.get_all_jodis() # Assuming kalyan_engine has this method
        jodi_freq = recent_data['jodi'].value_counts(normalize=True)
        
        hot_jodis = [j for j, freq in jodi_freq.items() if freq > jodi_freq.mean()]
        cold_jodis = [j for j, freq in jodi_freq.items() if freq < jodi_freq.mean()]

        # Streak Detection (simplified: last N consecutive appearances)
        def detect_streak(series, value, min_streak=3):
            streaks = (series == value).astype(int).groupby((series != value).cumsum()).cumsum()
            if not streaks.empty and streaks.max() >= min_streak:
                return streaks.max()
            return 0
        
        jodi_streaks = {}
        for jodi in all_jodis:
            streak = detect_streak(self.df['jodi'], jodi)
            if streak > 0:
                jodi_streaks[jodi] = streak

        return {
            "hot_digits": hot_digits,
            "cold_digits": cold_digits,
            "hot_jodis": hot_jodis,
            "cold_jodis": cold_jodis,
            "jodi_streaks": jodi_streaks
        }

    def get_pattern_based_predictions(self, target_date: datetime) -> List[str]:
        """
        Aggregates insights from all pattern analyses to suggest predictions.
        This method needs further refinement to weigh and combine these patterns effectively.
        """
        predictions = []

        # Digit Sums
        digit_sums = self.get_digit_sum_patterns()
        # Example: if a particular sum appears very frequently, jodis with that sum might be favored
        # For now, let's just take some digits that appear frequently as sums.
        # This part requires a method `get_all_jodis` in `kalyan_engine` which doesn't exist yet.
        # For now, we'll keep it as a placeholder.
        all_jodis_possible = [f"{i}{j}" for i in range(10) for j in range(10)] # Placeholder
        for freq_map in [digit_sums['open_sum_freq'], digit_sums['close_sum_freq'], digit_sums['jodi_sum_freq']]:
            if freq_map:
                top_sum_digits = sorted(freq_map, key=freq_map.get, reverse=True)[:2]
                for sd in top_sum_digits:
                    predictions.extend([j for j in all_jodis_possible if self._calculate_digit_sum(j) == sd])

        # Mirror Jodis
        mirror_jodis = self.get_mirror_jodi_patterns()
        predictions.extend(mirror_jodis)

        # Weekday Biases
        weekday_biases = self.get_weekday_biases()
        current_weekday = target_date.strftime('%A')
        if current_weekday in weekday_biases:
            day_bias = weekday_biases[current_weekday]
            if day_bias["jodi_freq"]:
                top_jodis_weekday = sorted(day_bias["jodi_freq"], key=day_bias["jodi_freq"].get, reverse=True)[:2]
                predictions.extend(top_jodis_weekday)
            
        # Hot/Cold Streaks
        streaks = self.get_hot_cold_streak_detection()
        predictions.extend(streaks['hot_jodis'])
        
        # Remove duplicates and return a limited list
        return list(pd.Series(predictions).unique())[:10]
