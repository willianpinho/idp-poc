"""IDP App - Streamlit UI Entry Point."""

import streamlit as st

st.set_page_config(
    page_title="IDP App - Intelligent Document Processing",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

st.sidebar.title("IDP App")
st.sidebar.caption("Intelligent Document Processing")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Upload", "Documents", "Review Queue"],
    label_visibility="collapsed",
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small style='color: gray;'>Powered by Anthropic Claude</small>",
    unsafe_allow_html=True,
)

if page == "Upload":
    from views.upload import render
    render(API_URL)
elif page == "Documents":
    from views.documents import render
    render(API_URL)
elif page == "Review Queue":
    from views.review import render
    render(API_URL)
