import streamlit as st

st.title("Palms Analysis:")

st.write("""
#### Inroduction:

BNI Palms Analysis is a Python-based web application designed to analyze BNI Palms slip-audit reports. It allows you to upload a chapters 
slip audit reports to generate data on One to Ones, referrals and their corelations with your chapter.
""")

st.write("""
#### To use this application, follow these steps:

1. Download all slip audit reports from BNI Connect.
2. Download your member's details from BNI Connect.
3. Upload the Excel slip-audit-reports and member details to this application in the "Palms Analysis" page. Please note that these
reports must be in .xls or .xlsx format. Follow the details below to get the expected files.
4. Click the "Get Reports" button to generate your reports.
5. Download whichever reports you need!
""")

st.write("""
#### How to get your slip audit reports:

1. Go to https://bniconnectglobal.com/
2. Click on Operations -> Chapter
3. Go to "Meeting Managment"
4. Go to "View Palms Summary"
5. Enter the dates from which you want to get the slip audit reports.
6. Click "completed" in the status section of this page. You should get a pop up of that slip audit report.
7. Scroll to the bottom and click on "Slips audit report". You should get another pop up.
8. Click "Export without Headers", which will download the slip audit report for you.
""")

st.write("""
#### How to get your member details:

1. Go to https://bniconnectglobal.com/
2. Click on Reports -> Chapter
3. Go to "Summary Palms Report"
4. Enter the current date and click go.
8. Click "Export without Headers", which will download the member details for you.
""")