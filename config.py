# Global Project Configuration

# Prediction Model Parameters
RECENT_WINDOW = 30 # Days
LONG_TERM_WINDOW = 180 # Days
MIN_FREQUENCY_THRESHOLD = 0.01

# Model Selection
MODEL_TYPE = "ensemble" # Options: "heat", "matrix", "ensemble"

# Ensemble Weights
ENSEMBLE_WEIGHTS = {
    "heat": 0.40,
    "matrix": 0.35,
    "momentum": 0.25
}

# Matrix Model Parameters
MATRIX_WINDOW_DAYS = 60

# Momentum Parameters
MOMENTUM_WINDOW = 7

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
