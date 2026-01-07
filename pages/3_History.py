import streamlit as st
from pathlib import Path

from core.file import File
from core.auth import require_login

require_login()

st.title("History")
st.caption("Restore application state from previous uploads")

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "db" / "upload"

if not UPLOAD_DIR.exists():
    st.info("No upload history found.")
    st.stop()

# =========================
# Discover runs
# =========================
run_dirs = sorted(
    [d for d in UPLOAD_DIR.iterdir() if d.is_dir()],
    reverse=True
)

if not run_dirs:
    st.info("No previous runs available.")
    st.stop()

# =========================
# Select run (LIST OPTION)
# =========================
run_id = st.selectbox(
    "Select a previous run to restore",
    options=[d.name for d in run_dirs]
)

run_path = UPLOAD_DIR / run_id
upload_files = sorted(run_path.glob("*.txt"))

if not upload_files:
    st.warning("Selected run contains no uploaded files.")
    st.stop()

# =========================
# Preview
# =========================
st.markdown(f"### Uploaded files in run `{run_id}`")
for p in upload_files:
    st.write(f"- {p.name}")

# =========================
# Restore state
# =========================
st.divider()

if st.button("🔄 Restore this run"):
    files = []

    with st.spinner("Restoring state from uploaded files..."):
        for p in upload_files:
            f = File.from_txt(p, display_name=p.name)
            files.append(f)

    st.session_state["files"] = files
    st.session_state["current_run_id"] = run_id

    st.success(f"Run `{run_id}` restored successfully.")
    st.info("You can now navigate to **File Overview**, **Plotting**, or **Sweeping**.")
