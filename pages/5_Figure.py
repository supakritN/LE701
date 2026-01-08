import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.auth import require_login

require_login()

st.title("Plotting (Plotly)")
st.caption("Interactive S2,1 plotting")

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
    Build legend label.
    - If sweep_param is selected: show only that param
    - Otherwise: show full config
    """
    if sweep_param and sweep_param in r.config:
        return f"{sweep_param}={r.config[sweep_param]}"
    else:
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

# ============================================================
# Select sweep parameter (LEGEND ONLY)
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
# Filter bar
# ============================================================
st.subheader("Calculation result")
st.caption("Filter format: column=value column=value (space separated)")

filter_text = st.text_input(
    "Filter",
    placeholder="er=3 tan_delta=0.02"
)

try:
    filtered_results = filter_results(f.results, filter_text)
except Exception as e:
    st.error(f"Filter error: {e}")
    st.stop()

if not filtered_results:
    st.warning("No results match the filter.")
    st.stop()

# ============================================================
# Build plot map (NO filtering by sweep)
# ============================================================
plot_map = {}
for i, r in enumerate(filtered_results, 1):
    label = build_legend_label(r, sweep_param)
    plot_map[f"[{i}] {label}"] = r

all_keys = list(plot_map.keys())

# ============================================================
# Plot options
# ============================================================
plot_mode = st.radio(
    "Plot type",
    options=["Raw S21 (Line)", "Custom X–Y"],
    horizontal=True
)

if plot_mode == "Custom X–Y":
    st.markdown(
        """
        **Variables**
        - `freq` : frequency array (GHz)
        - `s21`  : S2,1 magnitude (dB)
        - `np`   : NumPy
        """
    )
    custom_x = st.text_input("X expression", value="freq")
    custom_y = st.text_input("Y expression", value="s21")
else:
    custom_x = custom_y = None

# ============================================================
# Result selection
# ============================================================
selected = st.multiselect(
    "Select result(s)",
    options=all_keys,
    default=all_keys
)

# ============================================================
# Plot
# ============================================================
if selected and st.button("Plot"):
    fig = go.Figure()

    for key in selected:
        r = plot_map[key]

        freq = np.array([p[0] for p in r.data])
        s21 = np.array([p[1] for p in r.data])

        # ----------------------------------------------------
        # RAW → line plot
        # ----------------------------------------------------
        if plot_mode.startswith("Raw"):
            fig.add_trace(go.Scatter(
                x=freq,
                y=s21,
                mode="lines",
                name=key
            ))

        # ----------------------------------------------------
        # CUSTOM X–Y
        # ----------------------------------------------------
        else:
            try:
                scope = {"freq": freq, "s21": s21, "np": np}
                x = eval(custom_x, {}, scope)
                y = eval(custom_y, {}, scope)
            except Exception as e:
                st.error(f"{key}: {e}")
                continue

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=key
            ))

    # ========================================================
    # Layout
    # ========================================================
    fig.update_layout(
        title=f.display_name,
        xaxis_title="Frequency (GHz)" if plot_mode.startswith("Raw") else custom_x,
        yaxis_title="S2,1 (dB)" if plot_mode.startswith("Raw") else custom_y,
        legend_title="Legend",
        height=520
    )

    if plot_mode.startswith("Raw"):
        fig.update_yaxes(range=[-45, 0])

    # ========================================================
    # Render + built-in download
    # ========================================================
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f.display_name.replace(" ", "_"),
                "height": 520,
                "width": 900,
                "scale": 2
            }
        }
    )

