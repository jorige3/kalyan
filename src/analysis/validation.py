import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.engine.calendar import find_last_game_row, find_previous_game_row


def _normalize_jodi(value: Any) -> str:
    return str(value).zfill(2)


def _load_report_picks(report_path: Path) -> List[Dict[str, Any]]:
    with open(report_path, "r") as f:
        report = json.load(f)
    daily = report.get("daily_summary", {})
    picks = daily.get("top_picks_with_confidence")
    if not picks:
        picks = report.get("ranked_picks", [])
    return picks


def _load_logged_dates(log_path: Path) -> set:
    if not log_path.exists():
        return set()
    with open(log_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return {row.get("date") for row in reader if row.get("date")}


def _append_validation_row(log_path: Path, row: Dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = log_path.exists()
    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def validate_latest_game(
    df: pd.DataFrame,
    reports_dir: Path,
    log_path: Path,
) -> Optional[Dict[str, Any]]:
    """
    Validates the most recent actual game day against the previous game day's report.
    Skips non-game days and avoids duplicate log entries.
    """
    if df.empty:
        logging.warning("Validation skipped: no data available.")
        return None

    rows = df.sort_values("date").to_dict(orient="records")
    last_row = find_last_game_row(rows)
    if not last_row:
        logging.warning("Validation skipped: no game-day rows found.")
        return None

    prev_row = find_previous_game_row(rows, last_row["date"])
    if not prev_row:
        logging.warning("Validation skipped: no previous game-day row found.")
        return None

    actual_date = last_row["date"].strftime("%Y-%m-%d")
    prediction_date = prev_row["date"].strftime("%Y-%m-%d")

    existing_dates = _load_logged_dates(log_path)
    if actual_date in existing_dates:
        logging.info(f"Validation already logged for {actual_date}. Skipping.")
        return None

    report_path = reports_dir / f"kalyan_analysis_{prediction_date}.json"
    if not report_path.exists():
        logging.warning(f"Validation skipped: report not found for {prediction_date}.")
        return None

    picks = _load_report_picks(report_path)
    top5 = [_normalize_jodi(p.get("value")) for p in picks[:5]]
    actual_jodi = _normalize_jodi(last_row.get("jodi", ""))

    hit_rank = 0
    confidence = "Miss"
    if actual_jodi in top5:
        hit_rank = top5.index(actual_jodi) + 1
        confidence = next(
            (p.get("confidence", "Hit") for p in picks[:5] if _normalize_jodi(p.get("value")) == actual_jodi),
            "Hit"
        )

    row = {
        "date": actual_date,
        "prediction_date": prediction_date,
        "actual_jodi": actual_jodi,
        "predicted_top5": ",".join(top5),
        "hit_rank": hit_rank,
        "top1_hit": hit_rank == 1,
        "top3_hit": 1 <= hit_rank <= 3,
        "top5_hit": 1 <= hit_rank <= 5,
        "confidence": confidence,
        "report_path": str(report_path),
    }

    _append_validation_row(log_path, row)
    logging.info(f"Validation logged for {actual_date} using prediction {prediction_date}.")
    return row
