import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.auth import require_login
from math_utils.summary_table import build_summary_table

require_login()

st.title("Plotting")
st.caption("Frequency response and dual-band comparison")

# ============================================================
# Helpers
# ============================================================
def filter_results(results, filter_text):
    """
    Filter results by config using format:
    column=value column=value
    """
    if not filter_text.strip():
        return results

    conditions = filter_text.split()
    filtered = []

    for r in results:
        keep = True
        for cond in conditions:
            if "=" not in cond:
                raise ValueError(f"Invalid condition: {cond}")

            key, val = cond.split("=", 1)
            key = key.strip()
            val = val.strip()

            if key not in r.config:
                raise ValueError(f"Unknown config key: {key}")

            if str(r.config[key]) != val:
                keep = False
                break

        if keep:
            filtered.append(r)

    return filtered


def build_legend_label(r, sweep_param):
    """
    Legend behavior:
    - If sweep_param selected → show only that param
    - Else → show full config
    """
    if sweep_param and sweep_param in r.config:
        return f"{sweep_param}={r.config[sweep_param]}"
    return ", ".join(f"{k}={v}" for k, v in r.config.items())


# ============================================================
# State
# ============================================================
files = st.session_state.get("files", [])
if not files:
    st.info("Upload files or restore a run first.")
    st.stop()

# ============================================================
# File selection
# ============================================================
f = st.selectbox(
    "Select file",
    files,
    format_func=lambda x: x.display_name
)

results = f.results

# ============================================================
# Sweep parameter (LEGEND ONLY)
# ============================================================
if hasattr(f, "overview") and isinstance(f.overview, dict) and f.overview:
    sweep_param = st.selectbox(
        "Select sweep parameter (legend only)",
        ["(none)"] + list(f.overview.keys())
    )
    if sweep_param == "(none)":
        sweep_param = None
else:
    sweep_param = None

# ============================================================
# Filter bar (REQUIRED)
# ============================================================
st.subheader("Calculation result")
st.caption("Filter format: column=value column=value (space separated)")

filter_text = st.text_input(
    "Filter",
    placeholder="er=3 tan_delta=0.02"
)

try:
    filtered_results = filter_results(results, filter_text)
except Exception as e:
    st.error(f"Filter error: {e}")
    st.stop()

if not filtered_results:
    st.warning("No results match the filter.")
    st.stop()

# ============================================================
# Plot type
# ============================================================
plot_type = st.radio(
    "Plot type",
    ["Frequency × S2,1", "Compare 2 bands"],
    horizontal=True
)

# ============================================================
# -------- Frequency × S2,1 --------
# ============================================================
if plot_type == "Frequency × S2,1":

    selected = st.multiselect(
        "Select result(s)",
        options=list(range(len(filtered_results))),
        default=list(range(len(filtered_results))),
        format_func=lambda i: build_legend_label(
            filtered_results[i], sweep_param
        )
    )

    if st.button("Plot"):
        fig = go.Figure()

        for i in selected:
            r = filtered_results[i]
            freq = np.array([p[0] for p in r.data])
            s21 = np.array([p[1] for p in r.data])

            fig.add_trace(go.Scatter(
                x=freq,
                y=s21,
                mode="lines",
                name=build_legend_label(r, sweep_param)
            ))

        fig.update_layout(
            title=f.display_name,
            xaxis_title="Frequency (GHz)",
            yaxis_title="S2,1 (dB)",
            height=520
        )
        fig.update_yaxes(range=[-45, 0])

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": f.display_name.replace(" ", "_"),
                    "scale": 2
                }
            }
        )

# ============================================================
# -------- Compare 2 bands (USING SUMMARY TABLE) --------
# ============================================================
else:
    st.subheader("Compare 2 bands")

    # X parameter (sweep axis)
    x_param = st.selectbox(
        "X parameter",
        list(filtered_results[0].config.keys())
    )

    # Y metric
    y_metric = st.selectbox(
        "Y metric",
        ["s21", "Q", "fres"]
    )

    if st.button("Plot"):
        # --------------------------------------------
        # Build summary table (single source of truth)
        # --------------------------------------------
        try:
            df = build_summary_table(filtered_results, sweep_param=x_param)
        except Exception as e:
            st.error(f"Summary table error: {e}")
            st.stop()

        x = df[x_param]

        if y_metric == "s21":
            y_low = df["low_s21 (dB)"]
            y_high = df["high_s21 (dB)"]
            y_label = "S2,1 (dB)"

        elif y_metric == "Q":
            y_low = df["Q_low"]
            y_high = df["Q_high"]
            y_label = "Q"

        elif y_metric == "fres":
            y_low = df["low_fres (GHz)"]
            y_high = df["high_fres (GHz)"]
            y_label = "Resonant frequency (GHz)"

        else:
            st.stop()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x,
            y=y_low,
            mode="lines+markers",
            name="Low band"
        ))

        fig.add_trace(go.Scatter(
            x=x,
            y=y_high,
            mode="lines+markers",
            name="High band"
        ))

        fig.update_layout(
            title=f"{y_metric} vs {x_param}",
            xaxis_title=x_param,
            yaxis_title=y_label,
            height=520
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": f"{y_metric}_vs_{x_param}",
                    "scale": 2
                }
            }
        )
