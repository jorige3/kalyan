# Kalyan Analysis

CLI-driven analysis and reporting for Kalyan market data.

**Quick Start**
```bash
python main.py
```

**Install**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Data Format**
The default input file is `data/kalyan.csv` and must include:
- `date` in `YYYY-MM-DD`
- `open`
- `close`
- `jodi` (or it will be generated from `open` + `close`)
- `panel` or `sangam` (optional; used for sangam analysis)

Example:
```csv
date,open,close,jodi,panel
2026-02-09,7,7,77,458-250
2026-02-10,0,0,00,479-244
```

**Run Examples**
```bash
python main.py
python main.py --date 2026-02-11
python main.py --csv data/kalyan.csv
```

**Outputs**
- JSON snapshot: `reports/kalyan_analysis_YYYY-MM-DD.json`
- PDF report: `reports/kalyan_analysis_YYYY-MM-DD.pdf`
- Validation log: `reports/validation_log_v2.csv`

**JSON Snapshot Schema (reports/kalyan_analysis_YYYY-MM-DD.json)**
- `analysis_date` string `YYYY-MM-DD`
- `engine_version` string
- `generated_at` ISO timestamp
- `data`
- `data.source_file` path to CSV
- `data.record_count` integer
- `data.sha256` SHA-256 of CSV
- `daily_summary`
- `daily_summary.market_mood` string
- `daily_summary.analytical_confidence_score` integer
- `daily_summary.strongest_signals` list of picks
- `daily_summary.top_picks_with_confidence` list of picks
- `ranked_picks` list of picks

Pick object:
- `value` string
- `score` number
- `confidence` string (`High`, `Medium`, `Low`)
- `reasons` list of strings

**Calendar-Aware Validation**
- Validation runs by default on every run.
- It automatically skips non-game days (Sunday).
- Validation uses the previous game day’s report to score the latest actual game day.
- Disable validation: `python main.py --no-validate`

**Validation Log Schema (reports/validation_log_v2.csv)**
- `date` actual game date
- `prediction_date` report date used for prediction
- `actual_jodi` actual result
- `predicted_top5` comma-separated top 5 predictions
- `hit_rank` 1-5 if hit, 0 if miss
- `top1_hit` boolean
- `top3_hit` boolean
- `top5_hit` boolean
- `confidence` confidence label for the hit or `Miss`
- `report_path` path to the JSON report used

**Common Options**
- `--date YYYY-MM-DD` run analysis for a specific date
- `--csv data/kalyan.csv` use a custom CSV file
- `--no-validate` skip validation logging

**Troubleshooting**
- `No data available.` means the CSV is empty or not readable. Check `data/kalyan.csv`.
- Missing `reports/*.json` for a prediction date will skip validation for that day.
- If PDFs are not generated, make sure fonts exist in `fonts/` and `fpdf2` is installed.
- To reset validation history, use a new log path with `--validation-log`.
