import random
from typing import Dict, List

import pandas as pd


class MonteCarloAnalyzer:
    """
    Performs Monte Carlo simulations to assess the confidence of predictions.
    It simulates future outcomes based on historical patterns and evaluates
    how often current picks would have "hit" in these simulated scenarios.
    """

    def __init__(self, historical_df: pd.DataFrame):
        if not isinstance(historical_df, pd.DataFrame) or historical_df.empty:
            raise ValueError("Historical DataFrame cannot be empty or None.")
        self.historical_df = historical_df.copy()
        self._validate_dataframe()

    def _validate_dataframe(self):
        """Ensures the DataFrame has the necessary columns."""
        required_cols = ['date', 'jodi']
        if not all(col in self.historical_df.columns for col in required_cols):
            raise ValueError(f"Historical DataFrame must contain columns: {required_cols}")
        self.historical_df['date'] = pd.to_datetime(self.historical_df['date'])
        self.historical_df = self.historical_df.dropna(subset=['jodi']) # Drop rows with missing jodi

    def run_simulation(self, current_picks: List[str], num_simulations: int = 1000) -> Dict:
        """
        Runs Monte Carlo simulations to assess the hit rate of current_picks.
        
        Args:
            current_picks (List[str]): A list of the current top prediction Jodis.
            num_simulations (int): The number of Monte Carlo simulations to run.
            
        Returns:
            Dict: A dictionary containing simulation results, such as hit rates and confidence.
        """
        if not current_picks:
            return {"simulated_hit_rate": 0.0, "confidence_score": 0.0, "details": "No picks to simulate."}

        jodi_outcomes = self.historical_df['jodi'].dropna().tolist()
        if not jodi_outcomes:
            return {"simulated_hit_rate": 0.0, "confidence_score": 0.0, "details": "No historical jodi outcomes."}

        simulated_hits = 0

        for _ in range(num_simulations):
            # Randomly select a jodi from history for this simulation "day"
            simulated_outcome = random.choice(jodi_outcomes)
            if simulated_outcome in current_picks:
                simulated_hits += 1

        simulated_hit_rate = (simulated_hits / num_simulations) * 100

        # A simplistic confidence score based on hit rate - can be refined
        confidence_score = min(10, simulated_hit_rate / 10.0) # Scale 0-100 hit rate to 0-10 confidence

        return {
            "simulated_hit_rate": simulated_hit_rate,
            "confidence_score": confidence_score,
            "details": f"Simulated {num_simulations} days. {simulated_hits} hits for current picks."
        }

if __name__ == '__main__':
    # Example Usage
    dates = pd.to_datetime([f'2023-01-{i:02d}' for i in range(1, 31)])
    jodis = [f'{random.randint(0,9)}{random.randint(0,9)}' for _ in range(30)]
    dummy_historical_df = pd.DataFrame({'date': dates, 'jodi': jodis})

    current_picks_example = ["12", "34", "56"] # Example picks

    mc_analyzer = MonteCarloAnalyzer(dummy_historical_df)
    simulation_results = mc_analyzer.run_simulation(current_picks_example)

    print("Monte Carlo Simulation Results:")
    print(simulation_results)
