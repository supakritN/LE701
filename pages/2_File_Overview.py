import streamlit as st
from core.auth import require_login

require_login()

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

        # ---- minimal dip display ----
        f.analyze_bands_once()
        dip = f.dip_summary()["expected"]

        if dip is not None:
            st.markdown(f"**Resonance dips:** {dip}")

        # ---- sweep overview ----
        st.subheader("Sweep overview")

        if not f.overview:
            st.info("No valid sweep detected.")
            continue

        for sweep_param, df in f.overview.items():
            st.markdown(f"### Sweep candidate: `{sweep_param}`")
            st.table(df)
