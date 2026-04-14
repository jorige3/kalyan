"""
Markov Transition Model v1.0
Predicts the next Jodi based on the first-order Markov Chain transition probabilities:
P(Jodi_t | Jodi_t-1)
"""

import numpy as np
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MarkovModel:
    """
    Markov Transition Model for Jodi sequences.
    Calculates transition probabilities between consecutive Jodis.
    """

    def __init__(self, alpha=0.1):
        """
        Args:
            alpha (float): Laplace smoothing factor to handle unseen transitions.
        """
        self.alpha = alpha
        self.all_jodis = [f"{i:02d}" for i in range(100)]
        self.jodi_to_idx = {j: i for i, j in enumerate(self.all_jodis)}
        # 100x100 Transition Matrix
        self.transition_matrix = np.zeros((100, 100))

    def _train(self, jodi_sequence):
        """
        Populates the transition matrix from a sequence of Jodis.
        """
        self.transition_matrix.fill(0)
        
        # Convert sequence to indices
        indices = [self.jodi_to_idx.get(j) for j in jodi_sequence if j in self.jodi_to_idx]
        
        if len(indices) < 2:
            return

        # Count transitions
        for i in range(len(indices) - 1):
            curr_idx = indices[i]
            next_idx = indices[i + 1]
            self.transition_matrix[curr_idx, next_idx] += 1

        # Apply Laplace Smoothing: (count + alpha) / (total + 100 * alpha)
        # This ensures no zero probabilities for unseen transitions.
        row_sums = self.transition_matrix.sum(axis=1, keepdims=True)
        self.transition_matrix = (self.transition_matrix + self.alpha) / (
            row_sums + (100 * self.alpha)
        )

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts next Jodi probabilities based on the last observed Jodi.
        
        Args:
            df (pd.DataFrame): DataFrame containing at least a 'jodi' column.
            
        Returns:
            pd.DataFrame: DataFrame with 'jodi', 'score' (probability), and 'rank'.
        """
        if df.empty or "jodi" not in df.columns:
            logger.warning("MarkovModel: Empty DataFrame or missing 'jodi' column.")
            return pd.DataFrame()

        # Clean and ensure 2-digit strings
        jodis = df["jodi"].astype(str).str.zfill(2).tolist()
        
        if not jodis:
            return pd.DataFrame()

        # 1. Train on historical sequence
        self._train(jodis)

        # 2. Identify the current state (the last Jodi in the sequence)
        last_jodi = jodis[-1]
        if last_jodi not in self.jodi_to_idx:
            # Fallback to uniform distribution if last jodi is unknown
            scores = np.ones(100) / 100.0
        else:
            curr_idx = self.jodi_to_idx[last_jodi]
            scores = self.transition_matrix[curr_idx]

        # 3. Format output
        results = pd.DataFrame({
            "jodi": self.all_jodis,
            "score": scores
        })

        # Sort by probability and assign rank
        results = results.sort_values("score", ascending=False).reset_index(drop=True)
        results["rank"] = results.index + 1

        return results
