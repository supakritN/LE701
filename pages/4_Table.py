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
st.caption("Sweep-based resonance summary (baseline er = 1.0)")

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
# Select sweep parameter
# ============================================================

sweep_param = st.selectbox(
    "Select sweep parameter",
    list(f.overview.keys())
)

# ============================================================
# Build summary table
# ============================================================

df = build_summary_table(
    results=f.results,
    sweep_param=sweep_param
)

# ============================================================
# Filter bar
# ============================================================

st.subheader("Calculation result")
st.caption("Filter format: column=value (space separated)")

filter_text = st.text_input(
    "Filter",
    placeholder="er=2 tan_delta=0.02"
)

df_filtered = df

if filter_text.strip():
    try:
        conditions = filter_text.split()
        mask = pd.Series(True, index=df.index)

        for cond in conditions:
            if "=" not in cond:
                raise ValueError(f"Invalid condition: {cond}")

            col, val = cond.split("=", 1)
            col = col.strip()
            val = val.strip()

            if col not in df.columns:
                raise ValueError(f"Unknown column: {col}")

            if pd.api.types.is_numeric_dtype(df[col]):
                mask &= df[col] == float(val)
            else:
                mask &= df[col].astype(str) == val

        df_filtered = df[mask]

    except Exception as e:
        st.error(f"Filter error: {e}")
        st.stop()

# ============================================================
# Display table
# ============================================================

st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True
)
