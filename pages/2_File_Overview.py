import streamlit as st
from core.auth import require_login

require_login()

from math_utils.overview_table import build_overview_tables


st.title("File Overview")
st.caption("Overview of sweep parameters and result structure")

files = st.session_state.get("files", [])

if not files:
    st.info("No files available. Please upload and execute first.")
    st.stop()


for f in files:
    with st.expander(f"📄 {f.display_name}", expanded=False):

        st.markdown(f"**Total result blocks:** {len(f.results)}")

        if not f.results:
            st.info("No parsed results.")
            continue

        tables = build_overview_tables(
            [{"parameters": r.config} for r in f.results]
        )

        st.subheader("Sweep overview")

        if not tables:
            st.info("No valid sweep detected.")
        else:
            for sweep_param, df in tables.items():
                st.markdown(f"### Sweep candidate: `{sweep_param}`")
                st.table(df)
