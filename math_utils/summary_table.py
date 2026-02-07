import pandas as pd
from typing import List, Any

from math_utils.signal_feature import extract_dips
from math_utils.rf_metrics import (
    frequency_shift_MHz,
    sensitivity,
    window_size,
)


# ============================================================
# Summary table (complete, physics-correct, n-band)
# ============================================================

def build_summary_table(
    results: List[Any],
    sweep_param: str,
    er_base: float = 1.0,
) -> pd.DataFrame:

    rows = []

    # --------------------------------------------------------
    # Baseline f0 (only for permittivity sweep)
    # --------------------------------------------------------
    baseline_f0 = None
    if sweep_param == "er":
        for r in results:
            if sweep_param in r.config and r.config[sweep_param] == er_base:
                dips = extract_dips(r.data)
                baseline_f0 = [d.f0.f for d in dips]
                break

        if baseline_f0 is None:
            raise ValueError(f"Baseline er={er_base} not found")

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------
    for r in results:
        if sweep_param not in r.config:
            continue

        dips = extract_dips(r.data)
        row = {}

        # ----------------------------------------------------
        # Sweep parameter
        # ----------------------------------------------------
        row[sweep_param] = r.config[sweep_param]

        # ----------------------------------------------------
        # Per-band features
        # ----------------------------------------------------
        for i, dip in enumerate(dips):
            p = f"band{i+1}"

            # ---- geometry / signal
            row[f"{p}_f1_f(GHz)"] = dip.f1.f
            row[f"{p}_f1_s21(dB)"] = dip.f1.s21

            row[f"{p}_f0_f(GHz)"] = dip.f0.f
            row[f"{p}_f0_s21(dB)"] = dip.f0.s21

            row[f"{p}_f2_f(GHz)"] = dip.f2.f
            row[f"{p}_f2_s21(dB)"] = dip.f2.s21

            # ---- bandwidth & Q
            bw = dip.bw()
            q = dip.q()

            row[f"{p}_bw(GHz)"] = bw
            row[f"{p}_q"] = q
            row[f"{p}_1/q"] = dip.inv_q()

            # ------------------------------------------------
            # Frequency shift & sensitivities
            # ------------------------------------------------
            if sweep_param == "er":
                f0_base = baseline_f0[i]

                df_MHz = frequency_shift_MHz(dip, f0_base)
                row[f"{p}_f0-f0base(MHz)"] = df_MHz
                row[f"{p}_|f0-f0base|(MHz)"] = abs(df_MHz)

                er = r.config["er"]
                delta_er = er - er_base

                # ---- raw sensitivity (MHz / εr)
                row[f"{p}_sen_norm"] = sensitivity(
                    dip=dip,
                    f0_base=f0_base,
                    er=er,
                    er_base=er_base,
                )

            else:
                # ---- not applicable for other sweeps
                row[f"{p}_f0-f0base(MHz)"] = float("nan")
                row[f"{p}_|f0-f0base|(MHz)"] = float("nan")
                row[f"{p}_sen_norm"] = float("nan")

        # ----------------------------------------------------
        # Inter-band spacing
        # ----------------------------------------------------
        for i in range(len(dips) - 1):
            row[f"window_band{i+1}_{i+2}_GHz"] = window_size(
                dips[i], dips[i + 1]
            )

        # ----------------------------------------------------
        # Preserve ALL config parameters
        # ----------------------------------------------------
        for k, v in r.config.items():
            row[k] = v

        rows.append(row)

    # --------------------------------------------------------
    # Final DataFrame
    # --------------------------------------------------------
    return (
        pd.DataFrame(rows)
        .sort_values(sweep_param)
        .reset_index(drop=True)
    )
