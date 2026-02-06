def explain_pick(pick: int, signals: dict) -> list[str]:
    """
    Generates human-readable explanations for a given pick based on provided signals.

    Args:
        pick: The number (jodi) that was picked.
        signals: A dictionary containing lists of numbers for different signals.
                 Example:
                     {
                         "high_frequency": [65, 74],
                         "trend_window": [74, 35],
                         "extended_absence": [12],
                         "exhausted": [4],
                         "sangam_support": [74]
                     }

    Returns:
        A list of string explanations for why the pick was recommended.
    """
    reasons = []
    
    REASON_MAP = {
        "high_frequency": "High frequency in recent draws",
        "trend_window": "Appears in active trend window",
        "extended_absence": "Extended absence cycle (statistically due)",
        "exhausted": "⚠ Over-represented recently (exhaustion risk)",
        "sangam_support": "Supported by sangam pattern alignment"
    }

    if pick in signals.get("high_frequency", []):
        reasons.append(REASON_MAP["high_frequency"])

    if pick in signals.get("trend_window", []):
        reasons.append(REASON_MAP["trend_window"])

    if pick in signals.get("extended_absence", []):
        reasons.append(REASON_MAP["extended_absence"])

    if pick in signals.get("sangam_support", []):
        reasons.append(REASON_MAP["sangam_support"])

    if pick in signals.get("exhausted", []):
        reasons.append(REASON_MAP["exhausted"])

    return reasons
