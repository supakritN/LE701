import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.auth import require_login
from rf_math.rf_dualband import analyze_dualband_notch

require_login()

st.title("Sweeping Analysis")
st.caption("Dual-band −3 dB notch analysis (Bandwidth & Q factor)")

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
# Sweep parameter
# ============================================================
SWEEP_OPTIONS = {
    "er (permittivity)": "er",
    "tan_delta (loss tangent)": "tan_delta",
    "size": "size"
}

label = st.selectbox("Select sweep parameter", list(SWEEP_OPTIONS))
sweep_param = SWEEP_OPTIONS[label]

values = [r.config.get(sweep_param) for r in f.results if sweep_param in r.config]
values = sorted(set(values))

if len(values) < 2:
    st.error(f"`{sweep_param}` does not vary.")
    st.stop()

st.success(f"Sweeping `{sweep_param}` = {values}")

# ============================================================
# Frequency window
# ============================================================
st.subheader("Frequency window (GHz)")

all_freq = np.concatenate([
    np.array([p[0] for p in r.data]) for r in f.results
])

fmin, fmax = float(all_freq.min()), float(all_freq.max())

window = st.slider(
    "Analysis window",
    min_value=round(fmin, 2),
    max_value=round(fmax, 2),
    value=(round(fmin, 2), round(fmax, 2)),
    step=0.01
)

# ============================================================
# Analysis
# ============================================================
rows_low, rows_high = [], []

for r in f.results:
    if sweep_param not in r.config:
        continue

    freq = np.array([p[0] for p in r.data])
    s21 = np.array([p[1] for p in r.data])

    result = analyze_dualband_notch(freq, s21, window)
    if result is None:
        continue

    rows_low.append({
        sweep_param: r.config[sweep_param],
        "Q": result["low"]["Q"],
        "BW": result["low"]["bw"]
    })

    rows_high.append({
        sweep_param: r.config[sweep_param],
        "Q": result["high"]["Q"],
        "BW": result["high"]["bw"]
    })

df_low = pd.DataFrame(rows_low).sort_values(sweep_param)
df_high = pd.DataFrame(rows_high).sort_values(sweep_param)

if df_low.empty or df_high.empty:
    st.warning("No valid dual-band results.")
    st.stop()

# ============================================================
# Bandwidth plot
# ============================================================
st.subheader("Bandwidth vs sweep parameter")

fig_bw, ax_bw = plt.subplots()

ax_bw.plot(
    df_low[sweep_param], df_low["BW"],
    marker="s", color="black", label="Low band"
)
ax_bw.plot(
    df_high[sweep_param], df_high["BW"],
    marker="o", color="red", label="High band"
)

ax_bw.set_xlabel(sweep_param)
ax_bw.set_ylabel("Bandwidth (GHz)")
ax_bw.legend()
ax_bw.grid(True)

st.pyplot(fig_bw)

# ============================================================
# Q factor plot
# ============================================================
st.subheader("Q factor vs sweep parameter")

fig_q, ax_q = plt.subplots()

ax_q.plot(
    df_low[sweep_param], df_low["Q"],
    marker="s", color="black", label="Low band"
)
ax_q.plot(
    df_high[sweep_param], df_high["Q"],
    marker="o", color="red", label="High band"
)

ax_q.set_xlabel(sweep_param)
ax_q.set_ylabel("Q factor")
ax_q.legend()
ax_q.grid(True)

st.pyplot(fig_q)

