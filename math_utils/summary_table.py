import pandas as pd
from typing import List, Any

from math_utils.signal_feature import extract_bands
from math_utils.rf_metrics import (
    frequency_shift_MHz,
    sensitivity,
    window_size,
)


# ============================================================
# Summary table
# ============================================================

def build_summary_table(
    results: List[Any],
    sweep_param: str,
    er_base: float = 1.0,
) -> pd.DataFrame:
    """
    Build sweep-based resonance summary table.
    """

    rows = []
    baseline_f0 = None

    # --------------------------------------------------------
    # Find baseline ONLY if sweeping permittivity
    # --------------------------------------------------------
    if sweep_param == "er":
        for r in results:
            if sweep_param not in r.config:
                continue

            if r.config[sweep_param] == er_base:
                bands = extract_bands(r.data)
                baseline_f0 = [b.f0.f for b in bands]
                break

        if baseline_f0 is None:
            raise ValueError(f"Baseline er={er_base} not found")

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------
    for r in results:
        if sweep_param not in r.config:
            continue

        sweep_param_value = r.config[sweep_param]
        bands = extract_bands(r.data)

        row = {sweep_param: sweep_param_value}

        # ----------------------------------------------------
        # Per-band metrics
        # ----------------------------------------------------
        for i, band in enumerate(bands):
            prefix = f"band{i+1}"

            # ---- signal features
            row[f"{prefix}_f1_f(GHz)"] = band.f1.f
            row[f"{prefix}_f1_s21(dB)"] = band.f1.s21

            row[f"{prefix}_f0_f(GHz)"] = band.f0.f
            row[f"{prefix}_f0_s21(dB)"] = band.f0.s21

            row[f"{prefix}_f2_f(GHz)"] = band.f2.f
            row[f"{prefix}_f2_s21(dB)"] = band.f2.s21

            # ---- intrinsic RF metrics
            row[f"{prefix}_bw(GHz)"] = band.bw()
            row[f"{prefix}_q"] = band.q()
            row[f"{prefix}_1/q"] = band.inv_q()

            # ---- frequency shift (only valid if baseline exists)
            if sweep_param == "er":
                base_f0 = baseline_f0[i] if baseline_f0 is not None else None
                if base_f0 is not None:
                    shift_MHz = frequency_shift_MHz(band, base_f0)
                    row[f"{prefix}_Δf0(MHz)"] = shift_MHz
                    row[f"{prefix}_|Δf0|(MHz)"] = abs(shift_MHz)
                    
                    er = r.config["er"]
                    row[f"{prefix} Sensitivity (MHz/εr)"] = sensitivity(
                        shift_MHz=shift_MHz,
                        er=er,
                        er_base=er_base,
                        baseline_f0=base_f0,
                        norm=False,
                    )
                    row[f"{prefix} Sensitivity norm (MHz/εr)"] = sensitivity(
                        shift_MHz=shift_MHz,
                        er=er,
                        er_base=er_base,
                        baseline_f0=base_f0,
                        norm=True,
                    )
                else:
                    shift_MHz = float("nan")
                    row[f"{prefix}_Δf0(MHz)"] = float("nan")
                    row[f"{prefix}_|Δf0|(MHz)"] = float("nan")

                    row[f"{prefix} Sensitivity (MHz/εr)"] = float("nan")
                    row[f"{prefix} Sensitivity norm (MHz/εr)"] = float("nan")

        # ----------------------------------------------------
        # Inter-band spacing
        # ----------------------------------------------------
        for i in range(len(bands) - 1):
            row[f"window_band{i+1}–{i+2}(GHz)"] = window_size(
                bands[i], bands[i + 1]
            )

        # ----------------------------------------------------
        # Preserve config
        # ----------------------------------------------------
        for k, v in r.config.items():
            row[k] = v

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(sweep_param)
        .reset_index(drop=True)
    )
