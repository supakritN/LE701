import pandas as pd
from typing import List, Any

from math_utils.signal_feature import get_low_band, get_high_band

def bandwidth(f1: float, f2: float) -> float:
    """
    Bandwidth in GHz.
    """
    bw = f2 - f1
    if bw <= 0:
        raise ValueError("Bandwidth must be positive")
    return bw

def quality_factor(f0: float, bw: float) -> float:
    """
    Quality factor Q = f0 / BW.
    """
    if bw <= 0:
        raise ValueError("Bandwidth must be positive")
    return f0 / bw

def build_summary_table(
    results: List[Any],
    sweep_param: str,
    scope: float = 4.0
) -> pd.DataFrame:
    """
    Build resonance summary table for a sweep parameter.

    Units
    -----
    Frequency : GHz
    Δf        : MHz
    S21       : dB
    Q         : unitless
    Sensitivity : MHz / unit(sweep_param)
    """

    rows = []

    # ---------------------------------------------------------
    # Collect resonance data
    # ---------------------------------------------------------
    for r in results:
        if sweep_param not in r.config:
            continue

        param_value = r.config[sweep_param]

        low_f1, low_fres, low_f2 = get_low_band(r.data, scope=scope)
        high_f1, high_fres, high_f2 = get_high_band(r.data, scope=scope)

        bw_low = bandwidth(low_f1, low_f2)
        bw_high = bandwidth(high_f1, high_f2)

        q_low = quality_factor(low_fres, bw_low)
        q_high = quality_factor(high_fres, bw_high)

        rows.append({
            sweep_param: param_value,

            "low_f1 (GHz)": low_f1,
            "low_fres (GHz)": low_fres,
            "low_f2 (GHz)": low_f2,

            "high_f1 (GHz)": high_f1,
            "high_fres (GHz)": high_fres,
            "high_f2 (GHz)": high_f2,

            "BW_low (GHz)": bw_low,
            "BW_high (GHz)": bw_high,

            "Q_low": q_low,
            "Q_high": q_high,
        })

    if not rows:
        raise ValueError("No valid sweep data found")

    # ---------------------------------------------------------
    # Build DataFrame
    # ---------------------------------------------------------
    df = pd.DataFrame(rows).sort_values(sweep_param).reset_index(drop=True)

    # ---------------------------------------------------------
    # Δf (MHz) relative to baseline (first row)
    # ---------------------------------------------------------
    base_low_f = df.loc[0, "low_fres (GHz)"]
    base_high_f = df.loc[0, "high_fres (GHz)"]
    er_baseline = df.loc[0, "er"]

    df["Δf_low (MHz)"] = abs((df["low_fres (GHz)"] - base_low_f)) * 1000
    df["Δf_high (MHz)"] = abs((df["high_fres (GHz)"] - base_high_f)) * 1000

    df["low_sen (MHz/unit)"] = (df["Δf_low (MHz)"] / 10) / (df["er"] - er_baseline)
    df["high_sen (MHz/unit)"] = (df["Δf_high (MHz)"] / 10) / (df["er"] - er_baseline)

    df["low_sen_norm (GHz/unit)"] = df["low_sen (MHz/unit)"] / base_low_f
    df["high_sen_norm (GHz/unit)"] = df["high_sen (MHz/unit)"] / base_high_f

    return df
