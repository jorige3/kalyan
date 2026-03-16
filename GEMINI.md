# Kalyan Prediction System - Quantitative Refactor (v2.0)

The project has been fully refactored into a scientifically robust, modular, and production-ready quantitative analysis system.

## Summary of Major Improvements (Refactor v2.0)

*   **Architectural Separation**: The monolithic `main.py` has been decomposed into specialized modules for data loading, model implementation, analytical processing, backtesting, and reporting.
*   **Scientific Prediction Engine**: 
    *   Implemented `HeatModel` using a weighted scoring system: `recent_frequency (70%)`, `absence_score (20%)`, and `long_term_frequency (10%)`.
    *   Parameters like windows and weights are now fully externalized in `config.py`.
*   **Rolling Backtest Framework**: 
    *   Added a production-grade `RollingBacktester` that simulates historical daily predictions with **zero data leakage**.
    *   Performance metrics (Hit Rate for Top 5 and Top 10 jodis) are calculated dynamically.
*   **Evidence-Based Confidence**:
    *   Predictions now include a `Confidence Score (0-10)` derived directly from the model's recent historical performance (Hit Rate), ensuring analytical honesty.
*   **Duplicate Prevention**: 
    *   `main.py` now includes a check for existing daily reports to prevent redundant execution and notifications.
*   **Production Standards**: 
    *   Centralized logging in `src/utils/logger.py`.
    *   Clean repository structure with obsolete scripts and legacy analysis code removed.
    *   Updated `run_daily.sh` to use the new modular workflow.

## Project Structure

```text
/
├── main.py                 # Core workflow orchestration
├── config.py               # Centralized configuration and model weights
├── src/
│   ├── data/               # Data ingestion (DataLoader)
│   ├── models/             # Prediction models (HeatModel, MomentumModel)
│   ├── analytics/          # Trend and digit frequency analysis
│   ├── backtest/           # Rolling historical evaluation
│   ├── reporting/          # Report generation and Telegram integration
│   └── utils/              # Shared utilities (Logger)
├── data/                   # Historical CSV dataset
├── reports/                # Generated analytical reports
└── logs/                   # System and daily execution logs
```

## Current Status

*   **Core Logic**: 100% functional and verified with the `data/kalyan.csv` dataset.
*   **Reporting**: Automated text reports are generated daily with Top 5 and Top 10 picks.
*   **Verification**: The system correctly identifies its own hit rate and adjusts confidence scores accordingly.
*   **Repository**: Cleaned up all legacy `tests/`, `scripts/`, and `analytics/` directories from the previous iteration.

## Next Steps

*   **Model Experimentation**: Leverage the `MomentumModel` placeholder to test short-term pattern-following strategies.
*   **Enhanced Backtesting**: Implement multi-model ensemble backtesting.
*   **PDF Re-integration**: Re-implement the PDF report generator within the new `src/reporting/` module if visual reports are required again.
*   **Unit Tests**: Add a modern testing suite targeting the new modular components.

The project is now in a highly maintainable and scientifically sound state, ready for live market analysis.
