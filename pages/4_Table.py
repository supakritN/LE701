import streamlit as st
import pandas as pd

from core.auth import require_login
from math_utils.summary_table import build_summary_table

require_login()

st.title("Calculation Table")
st.caption("Permittivity sweep – resonance frequency shift")

# ============================================================
# Load session files
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

# ============================================================
# Sweep parameter
# ============================================================
SWEEP_OPTIONS = {
    "er (permittivity)": "er",
    "tan_delta (loss tangent)": "tan_delta",
    "size": "MUT_size"
}

label = st.selectbox("Select sweep parameter", list(SWEEP_OPTIONS))
sweep_param = SWEEP_OPTIONS[label]

values = [r.config.get(sweep_param) for r in f.results if sweep_param in r.config]
values = sorted(set(values))

if len(values) < 2:
    st.error(f"`{sweep_param}` does not vary.")
    st.stop()

# ============================================================
# Build table rows (math only)
# ============================================================
df = build_summary_table(
    results=f.results,
    sweep_param=sweep_param,
    scope=4.0
)

# ============================================================
# Display
# ============================================================
st.dataframe(df, use_container_width=True, hide_index=True)
