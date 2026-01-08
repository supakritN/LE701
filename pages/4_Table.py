import streamlit as st
import pandas as pd

from core.auth import require_login
from math_utils.summary_table import build_summary_table

# ============================================================
# Auth
# ============================================================
require_login()

# ============================================================
# Page header
# ============================================================
st.title("Calculation Table")
st.caption("Sweep-based resonance summary")

# ============================================================
# Load files
# ============================================================
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

# ============================================================
# Authoritative sweep overview
# ============================================================
overview_df = f.overview[sweep_param]
st.table(overview_df)

# ============================================================
# Extract fixed control variables (LOGIC ONLY)
# ============================================================
control_values = {
    row["Parameter"]: row["Value(s)"]
    for _, row in overview_df.iterrows()
    if not row["Parameter"].startswith("[SWEEP]")
}

# ============================================================
# Filter results → true 1-D sweep slice
# ============================================================
filtered_results = []

for r in f.results:
    # Must contain sweep parameter
    if sweep_param not in r.config:
        continue

    # Must match all fixed control variables
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
# Display result
# ============================================================
st.subheader("Calculation result")
st.dataframe(df, use_container_width=True, hide_index=True)

