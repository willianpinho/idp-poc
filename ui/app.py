"""PraxisIQ - Streamlit UI Entry Point."""

import streamlit as st

st.set_page_config(
    page_title="PraxisIQ - Intelligent Document Processing",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

st.sidebar.title("PraxisIQ")
st.sidebar.markdown("**Intelligent Document Processing**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Upload", "Documents", "Review Queue"],
    index=0,
)

if page == "Upload":
    from pages.upload import render
    render(API_URL)
elif page == "Documents":
    from pages.documents import render
    render(API_URL)
elif page == "Review Queue":
    from pages.review import render
    render(API_URL)
