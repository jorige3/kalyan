"""
Markov Transition Model v2.0 (Second-Order)
Predicts the next Jodi based on the last TWO observed Jodis:
P(Jodi_t | Jodi_t-2, Jodi_t-1)
Includes hierarchical fallback to First-Order and Global Frequency.
"""

from collections import defaultdict

import numpy as np
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MarkovV2Model:
    """
    Second-Order Markov Model with Laplace smoothing and hierarchical fallback.
    """

    def __init__(self, alpha=0.1):
        """
        Args:
            alpha (float): Laplace smoothing factor.
        """
        self.alpha = alpha
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        
        # Transition counters
        self.second_order = defaultdict(lambda: defaultdict(int)) # (j1, j2) -> j3
        self.first_order = defaultdict(lambda: defaultdict(int))  # j2 -> j3
        self.global_freq = defaultdict(int)                       # j3
        self.total_count = 0

    def _train(self, jodis):
        """
        Trains the hierarchical model on a sequence of Jodis.
        """
        self.second_order.clear()
        self.first_order.clear()
        self.global_freq.clear()
        self.total_count = len(jodis)

        for i in range(len(jodis)):
            j3 = jodis[i]
            self.global_freq[j3] += 1
            
            if i >= 1:
                j2 = jodis[i-1]
                self.first_order[j2][j3] += 1
                
                if i >= 2:
                    j1 = jodis[i-2]
                    self.second_order[(j1, j2)][j3] += 1

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts next Jodi using the second-order state with fallbacks.
        """
        if df.empty or "jodi" not in df.columns:
            return pd.DataFrame()

        # Ensure clean 2-digit strings
        jodis = df["jodi"].astype(str).str.zfill(2).tolist()
        if len(jodis) < 1:
            return pd.DataFrame()

        # 1. Train on historical data
        self._train(jodis)

        # 2. Determine Current State
        j_last = jodis[-1]
        j_penultimate = jodis[-2] if len(jodis) >= 2 else None
        
        scores = np.zeros(100)
        
        # 3. Hierarchical Probability Calculation
        # Check if we have second-order data for the current pair
        state_2 = (j_penultimate, j_last)
        if j_penultimate and state_2 in self.second_order:
            counts = self.second_order[state_2]
            total = sum(counts.values())
            for idx, j in enumerate(self.all_jodis):
                scores[idx] = (counts[j] + self.alpha) / (total + 100 * self.alpha)
        
        # Fallback 1: First-Order
        elif j_last in self.first_order:
            counts = self.first_order[j_last]
            total = sum(counts.values())
            for idx, j in enumerate(self.all_jodis):
                scores[idx] = (counts[j] + self.alpha) / (total + 100 * self.alpha)
        
        # Fallback 2: Global Frequency
        else:
            total = self.total_count
            for idx, j in enumerate(self.all_jodis):
                scores[idx] = (self.global_freq[j] + self.alpha) / (total + 100 * self.alpha)

        # 4. Format Result
        results = pd.DataFrame({
            "jodi": self.all_jodis,
            "score": scores
        })
        
        results = results.sort_values("score", ascending=False).reset_index(drop=True)
        results["rank"] = results.index + 1
        
        return results
