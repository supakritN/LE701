import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd

from core.file import File


# =========================
# CONFIG
# =========================
APP_PASSWORD = "Le7012026"

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "db"
UPLOAD_DIR = DB_DIR / "upload"
RESULT_DIR = DB_DIR / "results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

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

    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_upload_dir = UPLOAD_DIR / run_id
    run_result_dir = RESULT_DIR / run_id

    run_upload_dir.mkdir(parents=True, exist_ok=True)
    run_result_dir.mkdir(parents=True, exist_ok=True)

    with st.spinner("Processing files..."):
        for uploaded in uploaded_files:
            # ---------- Save uploaded file ----------
            upload_path = run_upload_dir / uploaded.name
            upload_path.write_bytes(uploaded.read())

            # ---------- Parse ----------
            f = File.from_txt(
                upload_path,
                display_name=uploaded.name
            )
            files.append(f)

            # ---------- Save CSV results ----------
            file_result_dir = run_result_dir / Path(uploaded.name).stem
            file_result_dir.mkdir(parents=True, exist_ok=True)

            csv_outputs = f.export_csv_bytes()
            for name, data in csv_outputs.items():
                (file_result_dir / name).write_bytes(data)

    st.success(f"Processed {len(files)} file(s).")
    st.markdown(f"**Run ID:** `{run_id}`")

    # =========================
    # DISPLAY RESULTS PER FILE
    # =========================
    for f in files:
        with st.expander(f"📄 File: {f.display_name}", expanded=False):

            st.markdown("### Summary")
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

            # ---- CSV Download (from memory, not disk) ----
            st.markdown("### Download output (CSV)")
            csv_outputs = f.export_csv_bytes()

            for name, data in csv_outputs.items():
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=data,
                    file_name=f"{Path(f.display_name).stem}_{name}",
                    mime="text/csv"
                )

