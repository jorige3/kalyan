"""
Refinement Script: Kalyan Ensemble Weight Optimization v3.0
Performs a sweep of weight combinations against historical data to maximize hit rates.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from src.backtest.rolling_backtester import RollingBacktester
from src.data.loader import DataLoader
from src.models.ensemble_model import EnsembleModel
from src.models.heat_model import HeatModel
from src.models.matrix_model import MatrixModel
from src.models.momentum_model import MomentumModel


def optimize():
    print("\n" + "=" * 60)
    print("🧪 QUANTITATIVE WEIGHT OPTIMIZATION - STARTING (v3.0)")
    print("=" * 60)

    # 1. Load Data
    loader = DataLoader(config.DATA_CSV_PATH)
    try:
        df = loader.load_data()
        print(f"Data Loaded: {len(df)} records for simulation.")
    except Exception as e:
        print(f"Failed to load data: {e}")
        sys.exit(1)

    # 2. Initialize Sub-models
    heat_model = HeatModel(
        recent_window=config.RECENT_WINDOW, long_term_window=config.LONG_TERM_WINDOW
    )
    matrix_model = MatrixModel(window=config.MATRIX_WINDOW_DAYS)
    momentum_model = MomentumModel(window=config.MOMENTUM_WINDOW)

    # 3. Define Weight Combinations to Test
    # [heat, matrix, momentum]
    test_weights = [
        {"heat": 0.40, "matrix": 0.35, "momentum": 0.25},  # Current (Balanced)
        {"heat": 0.50, "matrix": 0.30, "momentum": 0.20},  # Heat-Heavy
        {"heat": 0.30, "matrix": 0.50, "momentum": 0.20},  # Matrix-Heavy
        {"heat": 0.30, "matrix": 0.30, "momentum": 0.40},  # Momentum-Heavy
        {"heat": 0.33, "matrix": 0.33, "momentum": 0.34},  # Equal
    ]

    best_hit_rate = 0.0
    best_weights = None
    all_results = []

    # 4. Run Backtests
    for i, weights in enumerate(test_weights, 1):
        print(f"\nSimulation {i}/{len(test_weights)}: Weights = {weights}")
        ensemble_model = EnsembleModel(
            heat_model=heat_model,
            matrix_model=matrix_model,
            momentum_model=momentum_model,
            weights=weights,
        )

        # Use 365 days for robustness
        backtester = RollingBacktester(ensemble_model, window_days=365)
        results = backtester.run(df)

        if results:
            hit5 = results.get("hit_rate_top_5", 0) * 100
            hit10 = results.get("hit_rate_top_10", 0) * 100
            print(f"-> Top 5 Hit Rate: {hit5:.2f}% | Top 10 Hit Rate: {hit10:.2f}%")

            all_results.append({"id": i, "weights": weights, "hit5": hit5, "hit10": hit10})

            # Optimization Goal: Maximize Top 10 hit rate
            if hit10 > best_hit_rate:
                best_hit_rate = hit10
                best_weights = weights

    # 5. Report Findings
    print("\n" + "=" * 60)
    print("🏆 OPTIMIZATION SUMMARY")
    print("=" * 60)
    print(f"Winning Weights (Max Top 10): {best_weights}")
    print(f"Best Top 10 Performance: {best_hit_rate:.2f}%")
    print("-" * 60)

    # Simple recommendation
    print("\nRecommendation: Update config.py with these ENSEMBLE_WEIGHTS for production.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    optimize()
