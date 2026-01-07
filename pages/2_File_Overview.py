import streamlit as st
from core.auth import require_login

require_login()

import pandas as pd

st.title("File Overview")
st.caption("Summary of uploaded files and parsed result blocks")

files = st.session_state.get("files", [])

if not files:
    st.info("No files available. Please upload and execute first.")
    st.stop()

for f in files:
    with st.expander(f"📄 {f.display_name}", expanded=False):

        st.markdown(f"**Total Results:** {len(f.results)}")

        desc = f.results[0].description if f.results else []
        if desc:
            st.markdown(f"**X-axis:** {desc[0]}")
            if len(desc) > 1:
                st.markdown(f"**Y-axis:** {desc[1]}")

        # Independent parameters
        indep = f.independent_parameters()
        st.subheader("Independent parameter(s)")
        if indep:
            st.table(pd.DataFrame(
                [{"Parameter": k, "Values": sorted(set(v))} for k, v in indep.items()]
            ))
        else:
            st.write("None")

        # Control parameters
        ctrl = f.control_parameters()
        st.subheader("Control parameter(s)")
        if ctrl:
            st.table(pd.DataFrame(
                [{"Parameter": k, "Value": v} for k, v in ctrl.items()]
            ))
        else:
            st.write("None")

        # Result blocks
        st.subheader("Result blocks")
        rows = []
        for i, r in enumerate(f.results, 1):
            label = ", ".join(f"{k}={r.config[k]}" for k in indep) if indep else "fixed"
            rows.append({
                "Result ID": i,
                "Setting": label,
                "Points": r.count_data()
            })

        st.table(pd.DataFrame(rows))
