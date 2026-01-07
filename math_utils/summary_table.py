import pandas as pd
from typing import List, Any

from math_utils.signal_feature import get_low_band, get_high_band


def build_summary_table(
    results: List[Any],
    sweep_param: str,
    scope: float = 4.0
) -> pd.DataFrame:
    """
    Build resonance summary table for a sweep parameter.

    Columns
    -------
    sweep_param
    low_f1, low_fres, low_f2
    high_f1, high_fres, high_f2
    low_delta, high_delta

    Parameters
    ----------
    results : List[Result-like]
        Must have:
          - .config (dict)
          - .data   [(freq, s21)]
    sweep_param : str
        Parameter name to sweep (e.g. "er", "tan_delta", "MUT_size")
    scope : float
        Frequency separating low / high band (GHz)

    Returns
    -------
    pandas.DataFrame
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

        rows.append({
            sweep_param: param_value,

            "low_f1": low_f1,
            "low_fres": low_fres,
            "low_f2": low_f2,

            "high_f1": high_f1,
            "high_fres": high_fres,
            "high_f2": high_f2,
        })

    if not rows:
        raise ValueError("No valid sweep data found")

    # ---------------------------------------------------------
    # Build DataFrame
    # ---------------------------------------------------------
    df = pd.DataFrame(rows).sort_values(sweep_param).reset_index(drop=True)

    # ---------------------------------------------------------
    # Δf calculation (baseline = first row)
    # ---------------------------------------------------------
    base_low = df.loc[0, "low_fres"]
    base_high = df.loc[0, "high_fres"]

    df["low_delta"] = df["low_fres"] - base_low
    df["high_delta"] = df["high_fres"] - base_high

    return df
