import streamlit as st
import os
from pathlib import Path

# Directory to save uploaded files
SAVE_DIR_DATA = "Excel Files"
SAVE_DIR_NAME = "Member Names"
os.makedirs(SAVE_DIR_DATA, exist_ok=True)
os.makedirs(SAVE_DIR_NAME, exist_ok=True)

st.title("BNI PALMS Analysis")

# File uploader (accepting multiple files)
uploaded_files = st.file_uploader("Choose Excel slip-audit-reports", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = Path(SAVE_DIR_DATA) / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

uploaded_names = st.file_uploader("Choose Excel with member names", type=["xls", "xlsx"])

if uploaded_names:
    file_path = Path(SAVE_DIR_NAME) / uploaded_names.name
    with open(file_path, "wb") as f:
        f.write(uploaded_names.getbuffer())

