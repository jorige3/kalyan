"""
QUANTITATIVE WEIGHT OPTIMIZER v4.0 - INTELLIGENT ENSEMBLE TUNING (5-MODEL)
Refines ensemble weights for Heat, Matrix, Momentum, Markov, and Markov v2 models.
"""

import concurrent.futures
import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from tqdm import tqdm
except ImportError:
    # Minimal tqdm fallback if not installed
    def tqdm(iterable, **kwargs):
        return iterable


import config
from src.backtest.rolling_backtester import RollingBacktester
from src.data.loader import DataLoader
from src.models.ensemble_model import EnsembleModel
from src.models.heat_model import HeatModel
from src.models.markov_model import MarkovModel
from src.models.markov_v2_model import MarkovV2Model
from src.models.matrix_model import MatrixModel
from src.models.momentum_model import MomentumModel


def generate_weight_combinations(step=0.1):
    """
    Generates all valid combinations of 5 weights that sum to 1.0.
    Args:
        step (float): Step size for grid search (0.05 or 0.1)
    Returns:
        list[dict]: List of weight dictionaries
    """
    combinations = []
    # Using integer multiplication to avoid float precision issues
    s = int(step * 100)
    for h in range(0, 101, s):
        for m in range(0, 101 - h, s):
            for mo in range(0, 101 - h - m, s):
                for ma1 in range(0, 101 - h - m - mo, s):
                    ma2 = 100 - h - m - mo - ma1
                    combinations.append(
                        {
                            "heat": h / 100.0,
                            "matrix": m / 100.0,
                            "momentum": mo / 100.0,
                            "markov": ma1 / 100.0,
                            "markov_v2": ma2 / 100.0,
                        }
                    )
    return combinations


def calculate_optimization_score(results):
    """
    Multi-objective score: 70% Top 10 + 30% Top 5.
    """
    if not results:
        return 0.0
    hit5 = results.get("hit_rate_top_5", 0)
    hit10 = results.get("hit_rate_top_10", 0)
    return (hit10 * 0.7) + (hit5 * 0.3)


def run_single_backtest(df, weights, window_days=365):
    """
    Worker function for parallel execution. Evaluates the 5-model ensemble.
    """
    # Initialize all 5 sub-models
    heat_model = HeatModel(
        recent_window=config.RECENT_WINDOW, long_term_window=config.LONG_TERM_WINDOW
    )
    matrix_model = MatrixModel(window=config.MATRIX_WINDOW_DAYS)
    momentum_model = MomentumModel(window=config.MOMENTUM_WINDOW)
    markov_model = MarkovModel()
    markov_v2_model = MarkovV2Model()

    ensemble = EnsembleModel(
        heat_model=heat_model,
        matrix_model=matrix_model,
        momentum_model=momentum_model,
        markov_model=markov_model,
        markov_v2_model=markov_v2_model,
        weights=weights,
    )

    backtester = RollingBacktester(ensemble, window_days=window_days)
    results = backtester.run(df)
    score = calculate_optimization_score(results)

    return {"weights": weights, "results": results, "score": score}


def optimize(step=0.1, use_rolling_30=False, parallel=True):
    """
    Main optimization workflow for 5-model ensemble.
    """
    print("\n" + "=" * 75)
    print(
        f"🚀 QUANTITATIVE WEIGHT OPTIMIZATION v4.0 - {'ROLLING-30' if use_rolling_30 else 'STANDARD'} (5-MODEL)"
    )
    print("=" * 75)

    # 1. Load Data
    loader = DataLoader(config.DATA_CSV_PATH)
    try:
        df = loader.load_data()
        print(f"✅ Data Loaded: {len(df)} records.")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return

    window_days = 30 if use_rolling_30 else 365
    base_models = ["heat", "matrix", "momentum", "markov", "markov_v2"]

    # 2. Compute Individual Model Performance (Adaptive Weights Baseline)
    print("\n📊 STEP 1: Tracking Individual Model Performance...")
    model_baselines = {}

    for model_name in base_models:
        # Create weights that focus only on one model
        test_weights = {m: 0.0 for m in base_models}
        test_weights[model_name] = 1.0

        res = run_single_backtest(df, test_weights, window_days=window_days)
        hit10 = res["results"].get("hit_rate_top_10", 0)
        model_baselines[model_name] = hit10
        print(f"   -> {model_name.capitalize():<10} Baseline Top 10: {hit10:.2%}")

    # Calculate Adaptive Weights (Proportional to baseline performance)
    total_baseline = sum(model_baselines.values())
    if total_baseline > 0:
        adaptive_weights = {
            name: round(val / total_baseline, 3) for name, val in model_baselines.items()
        }
        # Normalize to ensure sum is exactly 1.0
        diff = round(1.0 - sum(adaptive_weights.values()), 3)
        adaptive_weights["markov_v2"] = round(adaptive_weights["markov_v2"] + diff, 3)
    else:
        adaptive_weights = {m: 0.20 for m in base_models}

    print("\n💡 Adaptive Weight Recommendation (Proportional to performance):")
    print(f"   {adaptive_weights}")

    # 3. Grid Search Optimization (5D)
    print("\n🔍 STEP 2: Running 5D Grid Search (Continuous Search)...")
    weight_combinations = generate_weight_combinations(step=step)
    all_results = []

    if parallel:
        print(
            f"   Starting parallel simulation ({len(weight_combinations)} combinations)..."
        )
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(run_single_backtest, df, w, window_days)
                for w in weight_combinations
            ]
            for f in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                all_results.append(f.result())
    else:
        print(
            f"   Starting sequential simulation ({len(weight_combinations)} combinations)..."
        )
        for w in tqdm(weight_combinations):
            all_results.append(run_single_backtest(df, w, window_days))

    # 4. Sorting and Identifying Best
    all_results.sort(key=lambda x: x["score"], reverse=True)
    best_config = all_results[0]
    top_5 = all_results[:5]

    # 5. Save Results
    output_path = "config_optimized.json"
    with open(output_path, "w") as f:
        json.dump(best_config["weights"], f, indent=4)

    # 6. Final Report
    print("\n" + "=" * 75)
    print("🏆 OPTIMIZATION REPORT (5-MODEL ENSEMBLE)")
    print("=" * 75)

    print("\n🌟 BEST CONFIGURATION FOUND:")
    print(f"   Score: {best_config['score']:.4f}")
    print(f"   Weights: {best_config['weights']}")
    print(f"   Hit Rate (Top 10): {best_config['results'].get('hit_rate_top_10', 0):.2%}")
    print(f"   Hit Rate (Top 5):  {best_config['results'].get('hit_rate_top_5', 0):.2%}")

    print("\n🔝 TOP 5 CONFIGURATIONS:")
    for i, res in enumerate(top_5, 1):
        w = res["weights"]
        s = res["score"]
        h10 = res["results"].get("hit_rate_top_10", 0)
        print(
            f"   #{i}: Score={s:.4f} | H:{w['heat']:.2f} M:{w['matrix']:.2f} Mo:{w['momentum']:.2f} M1:{w['markov']:.2f} M2:{w['markov_v2']:.2f} | Top10: {h10:.2%}"
        )

    print("\n✅ SUCCESS: Best weights saved to config_optimized.json")
    print("-" * 75)
    print("Final Recommended Weights for config.py:")
    print(f"ENSEMBLE_WEIGHTS = {best_config['weights']}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    # Check for CLI flags
    is_rolling = "--rolling-30" in sys.argv
    is_slow = "--sequential" in sys.argv

    # Set step size (0.1 for faster search, 0.05 for high precision)
    precision_step = 0.05 if "--high-precision" in sys.argv else 0.1

    optimize(step=precision_step, use_rolling_30=is_rolling, parallel=not is_slow)
