import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.auth import require_login
from rf_math.rf_metrics import analyze_notch_response

require_login()

st.title("Sweeping Analysis")
st.caption("Bandwidth and Quality Factor analysis (−3 dB notch method)")

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
# Sweep parameter selection
# ============================================================
SWEEP_OPTIONS = {
    "er (permittivity)": "er",
    "tan_delta (loss tangent)": "tan_delta",
    "size": "MUT_size"
}

sweep_label = st.selectbox(
    "Select sweep parameter",
    options=list(SWEEP_OPTIONS.keys())
)

sweep_param = SWEEP_OPTIONS[sweep_label]

# Validate sweep parameter
values = [
    r.config.get(sweep_param)
    for r in f.results
    if sweep_param in r.config
]

unique_values = sorted(set(values))

if len(unique_values) < 2:
    st.error(
        f"Sweep parameter `{sweep_param}` does not vary "
        f"(only one value found)."
    )
    st.stop()

st.success(
    f"Sweeping `{sweep_param}` with values: {unique_values}"
)

# ============================================================
# Frequency window
# ============================================================
st.subheader("Frequency window (GHz)")

all_freq = np.concatenate([
    np.array([p[0] for p in r.data])
    for r in f.results
])

f_min, f_max = float(all_freq.min()), float(all_freq.max())

window = st.slider(
    "Select analysis window",
    min_value=round(f_min, 2),
    max_value=round(f_max, 2),
    value=(round(f_min, 2), round(f_max, 2)),
    step=0.01
)

# ============================================================
# Analysis
# ============================================================
rows = []

for r in f.results:
    if sweep_param not in r.config:
        continue

    freq = np.array([p[0] for p in r.data])
    s21 = np.array([p[1] for p in r.data])

    result = analyze_notch_response(
        freq=freq,
        s21=s21,
        window=window
    )

    if result is None:
        continue

    rows.append({
        sweep_param: r.config[sweep_param],
        "f0 (GHz)": result["f0"],
        "BW (GHz)": result["bw"],
        "Q": result["q"]
    })

df = pd.DataFrame(rows).sort_values(sweep_param)

if df.empty:
    st.warning("No valid sweep results found in the selected window.")
    st.stop()

# ============================================================
# Results table
# ============================================================
st.subheader("Sweep results")
st.dataframe(df, use_container_width=True)

# ============================================================
# Sweep plots
# ============================================================
st.subheader("Sweep plots")

# ---- Q vs sweep parameter ----
fig_q, ax_q = plt.subplots()
ax_q.plot(df[sweep_param], df["Q"], marker="o")
ax_q.set_xlabel(sweep_param)
ax_q.set_ylabel("Quality Factor (Q)")
ax_q.grid(True)
st.pyplot(fig_q)

# ---- BW vs sweep parameter ----
fig_bw, ax_bw = plt.subplots()
ax_bw.plot(df[sweep_param], df["BW (GHz)"], marker="o")
ax_bw.set_xlabel(sweep_param)
ax_bw.set_ylabel("Bandwidth (GHz)")
ax_bw.grid(True)
st.pyplot(fig_bw)

# ============================================================
# S2,1 overlay plot
# ============================================================
st.subheader("S2,1 sweep overlay")

fig_s21, ax_s21 = plt.subplots(figsize=(8, 5))

for r in f.results:
    if sweep_param not in r.config:
        continue

    freq = np.array([p[0] for p in r.data])
    s21 = np.array([p[1] for p in r.data])

    mask = (freq >= window[0]) & (freq <= window[1])

    ax_s21.plot(
        freq[mask],
        s21[mask],
        label=f"{sweep_param}={r.config[sweep_param]}"
    )

ax_s21.set_xlabel("Frequency (GHz)")
ax_s21.set_ylabel("S2,1 (dB)")
ax_s21.set_xlim(window)
ax_s21.set_ylim(-45, 0)

ax_s21.legend(
    loc="center left",
    bbox_to_anchor=(1.02, 0.5)
)

ax_s21.grid(True)
st.pyplot(fig_s21)

