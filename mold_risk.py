def critical_relative_humidity(temp_c):
    """Simplified critical-RH curve (a practical approximation of the
    Sedlbauer/WUFI-Bio "LIM" isopleth used for mould-risk assessment on
    Swedish attic/crawlspace constructions): the relative humidity level
    at a given temperature above which mould growth becomes a real risk.
    Colder air can hold less moisture before condensation/mould-friendly
    conditions occur, so the critical threshold rises as temperature drops;
    below freezing, biological growth effectively stops."""
    if temp_c < 0:
        return 100.0
    if temp_c <= 20:
        return 98.0 - 0.9 * temp_c
    return 80.0


def mold_risk_ratio(temp_c, humidity_pct):
    """Ratio of actual relative humidity to the critical RH at this
    temperature. <0.70 = low risk, 0.70-0.95 = elevated, >0.95 = high.
    Returns None if the ratio can't be computed."""
    if temp_c is None or humidity_pct is None:
        return None
    crit = critical_relative_humidity(temp_c)
    if crit <= 0:
        return None
    return humidity_pct / crit


def risk_level(ratio):
    """Returns (level_name, color_hex) for a risk ratio from mold_risk_ratio."""
    if ratio is None:
        return "unknown", "#666666"
    if ratio < 0.70:
        return "low", "#2ECC71"
    if ratio < 0.95:
        return "elevated", "#F1C40F"
    return "high", "#E74C3C"
