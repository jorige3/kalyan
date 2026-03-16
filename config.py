# Global Project Configuration

# Prediction Model Parameters
RECENT_WINDOW = 30 # Days
LONG_TERM_WINDOW = 180 # Days
MIN_FREQUENCY_THRESHOLD = 0.01

# Ensemble Weights
ENSEMBLE_WEIGHTS = {
    "heat_model": 0.35,
    "digit_model": 0.25,
    "gap_model": 0.20,
    "mirror_model": 0.20
}

# Heat Model Parameters
HEAT_WEIGHTS = {
    "RECENT_FREQUENCY": 0.7,
    "ABSENCE_SCORE": 0.2,
    "LONG_TERM_FREQUENCY": 0.1
}

# Gap Cluster Parameters
GAP_MIN = 25
GAP_MAX = 40

# Mirror Window
MIRROR_WINDOW = 7

# Backtest Configuration
BACKTEST_START_DATE = None
BACKTEST_WINDOW_DAYS = 365

# Data Paths
DATA_CSV_PATH = "data/kalyan.csv"
REPORTS_DIR = "reports"

# Market Schedule
OFF_DAYS = ["Sunday"]
