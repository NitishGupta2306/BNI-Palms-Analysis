import streamlit as st
import subprocess
import os
from pathlib import Path

if "uploader_key_reports" not in st.session_state:
    st.session_state.uploader_key_reports = 0
if "uploader_key_names" not in st.session_state:
    st.session_state.uploader_key_names = 0

# Directory to save uploaded files
SAVE_DIR_DATA = "Excel Files"
SAVE_DIR_NAME = "Member Names"
DIR_REPORTS = "Reports"

# Create directories if they don't exist
os.makedirs(SAVE_DIR_DATA, exist_ok=True)
os.makedirs(SAVE_DIR_NAME, exist_ok=True)
os.makedirs(DIR_REPORTS, exist_ok=True)

st.title("BNI PALMS Analysis")


st.write("## Instructions:")
st.write("""
Note that files must be in .xls or .xlsx format

Follow these steps:
1. Upload Excel slip-audit-reports.
2. Upload Excel with member names.
3. Click the "Get Reports" button.
4. Download the reports.""")


st.write("## Upload Reports:")
# File uploader (accepting multiple files)
uploaded_files = st.file_uploader(
    "Choose Excel slip-audit-reports",
    type=["xls", "xlsx"],
    accept_multiple_files=True,
    key=f"reports_uploader_{st.session_state.uploader_key_reports}"
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = Path(SAVE_DIR_DATA) / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

uploaded_names = st.file_uploader(
    "Choose Excel with member names",
    type=["xls", "xlsx"],
    key=f"names_uploader_{st.session_state.uploader_key_names}"
)

if uploaded_names:
    file_path = Path(SAVE_DIR_NAME) / uploaded_names.name
    with open(file_path, "wb") as f:
        f.write(uploaded_names.getbuffer())

# State variable to keep track of report generation
if "reports_ready" not in st.session_state:
    st.session_state.reports_ready = False

# Button to trigger main.py
if st.button("Get Reports"):
    st.write("Running main.py...")
    result = subprocess.run(["python3", "main.py"], capture_output=True, text=True)
    st.write("## Output:")
    st.text(result.stdout)
    if result.stderr:
        st.error(result.stderr)
    else:
        # Delete all uploaded files after successful execution
        for file in os.listdir(SAVE_DIR_NAME):
            file_path = os.path.join(SAVE_DIR_NAME, file)
            os.remove(file_path)
        for file in os.listdir(SAVE_DIR_DATA):
            file_path = os.path.join(SAVE_DIR_DATA, file)
            os.remove(file_path)
        st.success("All uploaded files have been deleted.")

        # Mark reports as ready
        st.session_state.reports_ready = True

# Provide download buttons for each generated report if reports are ready
if st.session_state.reports_ready and os.listdir(DIR_REPORTS):
    st.write("## Download Reports")
    for file in os.listdir(DIR_REPORTS):
        file_path = os.path.join(DIR_REPORTS, file)
        with open(file_path, "rb") as f:
            st.download_button(label=f"Download {file}", data=f, file_name=file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.button("Clear Uploaded Files"):
    # Delete files from directories
    for folder in [SAVE_DIR_NAME, SAVE_DIR_DATA, DIR_REPORTS]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    # Clear session state
    for key in list(st.session_state.keys()):
        if key.startswith("uploaded_file") or key in ["reports_ready", "file_uploader"]:
            del st.session_state[key]

    # Increment uploader keys to reset widgets
    st.session_state.uploader_key_reports += 1
    st.session_state.uploader_key_names += 1

    # Force rerun
    st.rerun()