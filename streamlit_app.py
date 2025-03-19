import streamlit as st

# Page setup:
intro_page = st.Page(
    page = "views/introduction_page.py",
    title = "Introduction",
    icon = ":material/waving_hand:",
    default = True,
)

report_page = st.Page(
    page = "views/reports_page.py",
    title = "Palms Analysis",
    icon = ":material/partner_exchange:",
)

# Navigation setup:
pg = st.navigation(
    {
        "Info": [intro_page],
        "Reports": [report_page],
    }
)
pg.run()