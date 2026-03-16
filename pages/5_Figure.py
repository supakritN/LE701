import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.auth import require_login
from math_utils.summary_table import build_summary_table

require_login()

st.title("Plotting")
st.caption("Frequency response and dip-band comparison")

# ============================================================
# Helpers
# ============================================================

def filter_results(results, filter_text):

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

            if key not in r.config:
                raise ValueError(f"Unknown config key: {key}")

            if str(r.config[key]) != val:
                keep = False
                break

        if keep:
            filtered.append(r)

    return filtered


def build_legend_label(r, sweep_param):

    if sweep_param and sweep_param in r.config:
        return f"{sweep_param}={r.config[sweep_param]}"

    return ", ".join(f"{k}={v}" for k, v in r.config.items())


# ============================================================
# Load files
# ============================================================

files = st.session_state.get("files", [])

if not files:
    st.info("Upload files or restore a run first.")
    st.stop()

f = st.selectbox(
    "Select file",
    files,
    format_func=lambda x: x.display_name
)

results = f.results


# ============================================================
# Sweep parameter (legend)
# Default = first sweep parameter
# ============================================================

if hasattr(f, "overview") and isinstance(f.overview, dict) and f.overview:

    sweep_keys = list(f.overview.keys())

    sweep_param = st.selectbox(
        "Select sweep parameter (legend only)",
        sweep_keys,
        index=0
    )

else:

    sweep_param = list(results[0].config.keys())[0]
    st.write(f"Legend sweep parameter: **{sweep_param}**")


# ============================================================
# Filter results
# ============================================================

st.subheader("Calculation result")
st.caption("Filter format: column=value column=value")

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
    st.warning("No results match filter.")
    st.stop()


# ============================================================
# Build summary table
# ============================================================

try:

    df = build_summary_table(
        filtered_results,
        sweep_param=sweep_param
    )

except Exception as e:

    st.error(f"Summary table error: {e}")
    st.stop()


# ============================================================
# Plot type
# ============================================================

plot_type = st.radio(
    "Plot type",
    ["Frequency × S2,1", "Compare summary metrics"],
    horizontal=True
)


# ============================================================
# Frequency × S21
# ============================================================

if plot_type == "Frequency × S2,1":

    selected = st.multiselect(
        "Select result(s)",
        options=list(range(len(filtered_results))),
        default=list(range(len(filtered_results))),
        format_func=lambda i: build_legend_label(
            filtered_results[i],
            sweep_param
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

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# Compare summary metrics
# ============================================================

else:

    st.subheader("Compare summary metrics")

    if df.empty:
        st.warning("Summary table empty.")
        st.stop()

    columns = list(df.columns)

    # ------------------------------------------------
    # X axis default = sweep parameter
    # ------------------------------------------------

    x_index = columns.index(sweep_param) if sweep_param in columns else 0

    x_col = st.selectbox(
        "X axis",
        columns,
        index=x_index
    )

    # ------------------------------------------------
    # Y axis default = band1_q
    # ------------------------------------------------

    default_y = []

    if "band1_q" in columns:
        default_y = ["band1_q", "band2_q"]
    else:
        for c in columns:
            if "band1" in c and "q" in c.lower():
                default_y = [c]
                break

    y_cols = st.multiselect(
        "Y axis",
        columns,
        default=default_y
    )

    if not y_cols:
        st.warning("Select at least one Y column.")
        st.stop()

    # ------------------------------------------------
    # Plot
    # ------------------------------------------------

    if st.button("Plot"):

        fig = go.Figure()

        for col in y_cols:

            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="lines+markers",
                name=col
            ))

        fig.update_layout(
            title=f"{', '.join(y_cols)} vs {x_col}",
            xaxis_title=x_col,
            yaxis_title="Value",
            height=520
        )

        st.plotly_chart(fig, use_container_width=True)

    # # Optional debug
    # with st.expander("Show summary table"):
    #     st.dataframe(df)