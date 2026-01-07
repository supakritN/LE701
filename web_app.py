import streamlit as st
from pathlib import Path
import tempfile
import pandas as pd

from core.file import File


# =========================
# CONFIG
# =========================
APP_PASSWORD = "Le7012026"   # CHANGE THIS
st.set_page_config(
    page_title="S-Parameter Automation Tool",
    layout="wide"
)


# =========================
# AUTHENTICATION
# =========================
def require_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Login")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")

        st.stop()


require_login()


# =========================
# MAIN UI
# =========================
st.title("S-Parameter Automation Tool")

uploaded_files = st.file_uploader(
    "Upload S-parameter .txt files",
    type=["txt"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("Upload one or more .txt files to begin.")
    st.stop()


# =========================
# EXECUTION
# =========================
if st.button("Execute Calculation"):
    files: list[File] = []

    with st.spinner("Processing files..."):
        for uploaded in uploaded_files:
            # Write uploaded content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                tmp.write(uploaded.read())
                tmp_path = Path(tmp.name)

            # Preserve original filename for display
            f = File.from_txt(
                tmp_path,
                display_name=uploaded.name
            )
            files.append(f)

    st.success(f"Processed {len(files)} file(s).")

    # =========================
    # DISPLAY RESULTS PER FILE
    # =========================
    for f in files:
        with st.expander(f"📄 File: {f.display_name}", expanded=False):

            st.markdown(f"### Summary")
            st.markdown(f"**Results:** {len(f.results)}")

            if not f.results:
                st.warning("No results found in this file.")
                continue

            # ---- Axes ----
            desc = f.results[0].description
            if desc:
                st.markdown(f"**X-axis:** {desc[0]}")
                if len(desc) > 1:
                    st.markdown(f"**Y-axis:** {desc[1]}")

            # ---- Independent parameters ----
            st.markdown("### Independent parameter(s)")
            indep = f.independent_parameters()
            if indep:
                indep_rows = []
                for k, v in indep.items():
                    indep_rows.append({
                        "Parameter": k,
                        "Values": ", ".join(map(str, sorted(set(v))))
                    })
                st.table(pd.DataFrame(indep_rows))
            else:
                st.write("None")

            # ---- Control parameters ----
            st.markdown("### Control parameter(s)")
            ctrl = f.control_parameters()
            if ctrl:
                ctrl_df = pd.DataFrame(
                    [{"Parameter": k, "Value": v} for k, v in ctrl.items()]
                )
                st.table(ctrl_df)
            else:
                st.write("None")

            # ---- Results detail ----
            st.markdown("### Results detail")
            detail_rows = []
            for i, r in enumerate(f.results, 1):
                label = ", ".join(
                    f"{k}={r.config[k]}" for k in indep
                ) if indep else "fixed"

                detail_rows.append({
                    "Result ID": i,
                    "Independent setting": label,
                    "Points": r.count_data()
                })

            st.table(pd.DataFrame(detail_rows))

            # ---- CSV Download ----
            st.markdown("### Download output (CSV)")
            csv_outputs = f.export_csv_bytes()

            for name, data in csv_outputs.items():
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=data,
                    file_name=f"{Path(f.display_name).stem}_{name}",
                    mime="text/csv"
                )
