import streamlit as st
import pandas as pd

from core.auth import require_login
from math_utils.summary_table import build_summary_table

require_login()

st.title("Calculation Table")
st.caption("Sweep-based resonance summary")

files = st.session_state.get("files", [])

if not files:
    st.info("No files loaded. Please upload files first.")
    st.stop()

# ============================================================
# Select file
# ============================================================
f = st.selectbox(
    "Select file",
    files,
    format_func=lambda x: x.display_name
)

if not f.results:
    st.info("Selected file has no results.")
    st.stop()

if not f.overview:
    st.error("No valid sweep detected in this file.")
    st.stop()

# ============================================================
# Select sweep parameter (ONLY valid sweeps)
# ============================================================
sweep_param = st.selectbox(
    "Select sweep parameter",
    list(f.overview.keys())
)

overview_df = f.overview[sweep_param]

# ============================================================
# Extract control variables (authoritative)
# ============================================================
control_values = {}

for _, row in overview_df.iterrows():
    p = row["Parameter"]
    if not p.startswith("[SWEEP]"):
        control_values[p] = row["Value(s)"]

# ============================================================
# Show control variables
# ============================================================
st.subheader("Control variables (fixed)")

if control_values:
    st.table(pd.DataFrame([
        {"Parameter": k, "Value": v}
        for k, v in control_values.items()
    ]))
else:
    st.write("None")

# ============================================================
# Filter results → true 1-D sweep slice
# ============================================================
filtered_results = []

for r in f.results:
    # Must contain sweep param
    if sweep_param not in r.config:
        continue

    # Must match all fixed controls
    valid = True
    for k, v in control_values.items():
        if str(r.config.get(k)) != str(v):
            valid = False
            break

    if valid:
        filtered_results.append(r)

if len(filtered_results) < 2:
    st.error("Not enough valid sweep points after filtering.")
    st.stop()

# ============================================================
# Build calculation table (math only)
# ============================================================
df = build_summary_table(
    results=filtered_results,
    sweep_param=sweep_param,
    scope=4.0
)

# ============================================================
# Display
# ============================================================
st.dataframe(df, use_container_width=True, hide_index=True)
