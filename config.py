# Configuration for analysis
CYCLE_GAP_MAX_DAYS = 7 # Days a number hasn't appeared to be considered 'due'
DUE_THRESHOLD = 30 # Lookback days for due cycles
DUE_TOP_N = 5 # Not directly used in current due cycle logic, but kept for future expansion

HOT_LOOKBACK_DAYS = 30 # Days to look back for hot numbers
HOT_TOP_N = 3 # Top N hot digits/jodis

EXHAUSTED_LOOKBACK_DAYS = 30 # Days to look back for exhausted numbers
EXHAUSTED_GAP_THRESHOLD = 3 # Number of consecutive hits to consider exhausted (e.g., 3+ hits)
EXHAUSTED_BOTTOM_N = 3 # Not directly used in current exhausted logic, but kept for future expansion

TOP_PICKS_COUNT = 3 # Number of top picks to generate

# Monte Carlo Simulation
MONTE_CARLO_SIMULATIONS = 1000