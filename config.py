# Global Project Configuration

# Prediction Model Parameters
RECENT_WINDOW = 30 # Days
LONG_TERM_WINDOW = 180 # Days
MIN_FREQUENCY_THRESHOLD = 0.01 # Minimum relative frequency to be considered "Hot"

# Heat Model Weights
HEAT_WEIGHTS = {
    "RECENT_FREQUENCY": 0.7,
    "ABSENCE_SCORE": 0.2,
    "LONG_TERM_FREQUENCY": 0.1
}

# Backtest Configuration
BACKTEST_START_DATE = None # Use default (last year)
BACKTEST_WINDOW_DAYS = 365

# Data Paths
DATA_CSV_PATH = "data/kalyan.csv"
REPORTS_DIR = "reports"

# Telegram Configuration
# Credentials should be set in .env for security.
# TELEGRAM_BOT_TOKEN
# TELEGRAM_CHAT_ID

# Market Schedule
OFF_DAYS = ["Sunday"]
