import streamlit as st
from core.auth import require_login

require_login()

from pathlib import Path
from datetime import datetime
from core.file import File

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "db" / "upload"
RESULT_DIR = BASE_DIR / "db" / "results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

st.title("Upload")

uploaded_files = st.file_uploader(
    "Upload S-parameter .txt files",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files and st.button("Execute"):
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_upload_dir = UPLOAD_DIR / run_id
    run_upload_dir.mkdir(parents=True, exist_ok=True)

    files = []

    for uploaded in uploaded_files:
        path = run_upload_dir / uploaded.name
        path.write_bytes(uploaded.read())
        f = File.from_txt(path, display_name=uploaded.name)
        files.append(f)

    st.session_state["files"] = files
    st.session_state["current_run_id"] = run_id

    st.success(f"Run {run_id} completed.")
