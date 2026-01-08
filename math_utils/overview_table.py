# math_utils/overview_table.py

from collections import defaultdict
from typing import Dict, List, Any
import pandas as pd


def build_overview_tables(results: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Build sweep overview tables.

    Rules
    -----
    - Sweep candidate must have >1 unique value
    - Only FIXED parameters appear as controls
    - Varying non-sweep parameters are excluded

    Returns
    -------
    dict[str, DataFrame]
        One DataFrame per sweep candidate
    """

    if not results:
        return {}

    # Collect parameter values
    param_values = defaultdict(list)
    for block in results:
        for k, v in block.get("parameters", {}).items():
            param_values[k].append(v)

    tables = {}

    for sweep_param, sweep_vals_all in param_values.items():
        sweep_vals = sorted(set(sweep_vals_all))

        # Must be real sweep
        if len(sweep_vals) <= 1:
            continue

        rows = [{
            "Parameter": f"[SWEEP] {sweep_param}",
            "Value(s)": ", ".join(map(str, sweep_vals))
        }]

        # Fixed control parameters only
        for ctrl_param, ctrl_vals_all in param_values.items():
            if ctrl_param == sweep_param:
                continue

            ctrl_vals = sorted(set(ctrl_vals_all))
            if len(ctrl_vals) == 1:
                rows.append({
                    "Parameter": ctrl_param,
                    "Value(s)": str(ctrl_vals[0])
                })

        tables[sweep_param] = pd.DataFrame(rows)

    return tables
