import pandas as pd
from typing import List, Any

from math_utils.signal_feature import get_low_band, get_high_band


# ============================================================
# RF metrics
# ============================================================
def bandwidth(f1: float, f2: float) -> float:
    bw = f2 - f1
    if bw <= 0:
        raise ValueError("Bandwidth must be positive")
    return bw


def quality_factor(f0: float, bw: float) -> float:
    if bw <= 0:
        raise ValueError("Bandwidth must be positive")
    return f0 / bw


# ============================================================
# Summary table
# ============================================================
def build_summary_table(
    results: List[Any],
    sweep_param: str,
    scope: float = 4.0,
    normalize: bool = True
) -> pd.DataFrame:
    """
    Build resonance summary table.

    Units
    -----
    Frequency : GHz
    Δf        : MHz
    Q         : unitless
    Sensitivity : MHz / unit
    """

    rows = []

    # ---------------------------------------------------------
    # Collect resonance data
    # ---------------------------------------------------------
    for r in results:
        if sweep_param not in r.config:
            continue

        param_value = r.config[sweep_param]

        low_f1, low_fres, low_f2, low_s21 = get_low_band(r.data, scope=scope)
        high_f1, high_fres, high_f2, high_s21 = get_high_band(r.data, scope=scope)

        bw_low = bandwidth(low_f1, low_f2)
        bw_high = bandwidth(high_f1, high_f2)

        q_low = quality_factor(low_fres, bw_low)
        q_high = quality_factor(high_fres, bw_high)

        # -----------------------------------------------------
        # Base row (existing metrics)
        # -----------------------------------------------------
        row = {
            sweep_param: param_value,

            "low_f1 (GHz)": low_f1,
            "low_fres (GHz)": low_fres,
            "low_f2 (GHz)": low_f2,
            "low_s21 (dB)": low_s21,

            "high_f1 (GHz)": high_f1,
            "high_fres (GHz)": high_fres,
            "high_f2 (GHz)": high_f2,
            "high_s21 (dB)": high_s21,

            "BW_low (GHz)": bw_low,
            "BW_high (GHz)": bw_high,

            "Q_low": q_low,
            "Q_high": q_high,
        }

        # -----------------------------------------------------
        # ADD CONFIG (hidden-by-default intent)
        # -----------------------------------------------------
        for k, v in r.config.items():
            row[f"{k}"] = v

        rows.append(row)

    if not rows:
        raise ValueError("No valid sweep data found")

    # ---------------------------------------------------------
    # Build DataFrame
    # ---------------------------------------------------------
    df = pd.DataFrame(rows).sort_values(sweep_param).reset_index(drop=True)

    # ---------------------------------------------------------
    # Δf (MHz) relative to baseline
    # ---------------------------------------------------------
    base_low_f = df.loc[0, "low_fres (GHz)"]
    base_high_f = df.loc[0, "high_fres (GHz)"]
    base_param = df.loc[0, sweep_param]

    df["Δf_low (MHz)"] = (df["low_fres (GHz)"] - base_low_f).abs() * 1000
    df["Δf_high (MHz)"] = (df["high_fres (GHz)"] - base_high_f).abs() * 1000

    # ---------------------------------------------------------
    # Sensitivity
    # ---------------------------------------------------------
    low_sen = []
    high_sen = []
    low_sen_norm = []
    high_sen_norm = []

    for p, dfl, dfh in zip(
        df[sweep_param],
        df["Δf_low (MHz)"],
        df["Δf_high (MHz)"]
    ):
        if p == base_param:
            low_sen.append("N/A")
            high_sen.append("N/A")
            low_sen_norm.append("N/A")
            high_sen_norm.append("N/A")
            continue

        sen_low = dfl / abs(p - base_param)
        sen_high = dfh / abs(p - base_param)

        low_sen.append(sen_low)
        high_sen.append(sen_high)

        if normalize:
            low_sen_norm.append(sen_low / base_low_f)
            high_sen_norm.append(sen_high / base_high_f)
        else:
            low_sen_norm.append("N/A")
            high_sen_norm.append("N/A")

    df["low_sen (MHz/unit)"] = low_sen
    df["high_sen (MHz/unit)"] = high_sen
    df["low_sen_norm (1/unit)"] = low_sen_norm
    df["high_sen_norm (1/unit)"] = high_sen_norm

    return df

