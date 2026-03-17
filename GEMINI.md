# Kalyan Prediction System - Probabilistic Ensemble (v3.0)

The system has been upgraded to a hybrid ensemble architecture, combining longitudinal frequency analysis with probabilistic digit matrices and conditional panel state logic.

## Summary of Major Improvements (v3.0 - Probabilistic Matrix)

*   **Jodi Probability Matrix Model**:
    - **Base Probability**: Calculates joint probability $P(A) \cdot P(B)$ for all 100 jodis based on historical digit distributions.
    - **Conditional Panel Logic**: Implements a conditional state model $P(digit \mid prev\_panel\_last\_digit)$, using the last digit of the previous day's panels as a statistical pointer.
    - **Hybrid Scoring**: Merges base and conditional probabilities ($0.6$ base / $0.4$ conditional) to target "statistically ripe" combinations.

*   **Advanced Ensemble Architecture**:
    - Transitioned to a 3-pillar ensemble:
      - **Heat Model (40%)**: Captures frequency, absence, and long-term trends.
      - **Matrix Model (35%)**: Probabilistic digit distribution and panel-conditional behavior.
      - **Momentum Model (25%)**: Short-term pattern following (7-day window).
    - **Global Normalization**: All model scores are normalized to $[0, 1]$ before weighting to ensure fair signal contribution.

*   **Dynamic Confidence Scoring**:
    - Integrated a 1-10 confidence scale mapped directly to the Top 10 hit rate from a 365-day rolling backtest.
    - Ensures users see realistic expectations based on current model performance.

*   **Production Enhancements**:
    - Standardized output format for console and reporting.
    - Configurable model selection (`heat`, `matrix`, or `ensemble`) via `config.py`.
    - Enhanced `RollingBacktester` with yearly performance breakdowns and no data leakage.

## Project Structure

```text
/
├── main.py                 # Workflow orchestration with model selection
├── config.py               # Ensemble weights, model parameters, and model selection
├── src/
│   ├── analytics/
│   │   └── jodi_matrix.py  # Probabilistic and conditional matrix logic
│   ├── models/             # Specialized Models
│   │   ├── matrix_model.py # Probabilistic Matrix implementation
│   │   ├── ensemble_model.py
│   │   ├── heat_model.py
│   │   └── momentum_model.py
│   ├── backtest/
│   │   └── rolling_backtester.py # Multi-model backtesting with yearly breakdown
...
```

## Current Status

*   **Ensemble Engine (v3.0)**: Fully operational with Heat, Matrix, and Momentum signals.
*   **Backtesting**: Verified Top 10 performance with real-world datasets.
*   **Documentation**: Updated to reflect probabilistic standards.

## Next Steps

- **Panel Predictor**: Extend the matrix model to predict full 3-digit panels using similar conditional logic.
- **Auto-weighting**: Implement a Bayesian optimizer to dynamically adjust ensemble weights based on recent backtest performance.
- **Validation**: Continue monitoring Top 10 hit rates to refine conditional probability weights.

The project is now in a production-grade state, leveraging advanced statistical techniques for Kalyan market analysis.
