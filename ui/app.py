"""PraxisIQ - Streamlit UI Entry Point.

Navigation uses URL query params (``?page=upload``) instead of path-based
routes. Streamlit ships as a single-page app served from ``/``; any path-based
navigation (e.g. ``/upload``) breaks relative asset paths in the frontend
bundle and yields 404s for ``_stcore/host-config`` and ``_stcore/health``.
"""

import streamlit as st

st.set_page_config(
    page_title="PraxisIQ - Intelligent Document Processing",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# Map of nav labels to query-param slugs. Order defines sidebar order.
PAGES: dict[str, str] = {
    "Upload": "upload",
    "Documents": "documents",
    "Review Queue": "review",
}
SLUG_TO_LABEL: dict[str, str] = {slug: label for label, slug in PAGES.items()}
DEFAULT_LABEL = "Upload"


def _current_label_from_query() -> str:
    """Return the nav label encoded in ``?page=...``, falling back to default."""
    slug = st.query_params.get("page", PAGES[DEFAULT_LABEL])
    return SLUG_TO_LABEL.get(slug, DEFAULT_LABEL)


st.sidebar.title("PraxisIQ")
st.sidebar.markdown("**Intelligent Document Processing**")
st.sidebar.markdown("---")

current_label = _current_label_from_query()
labels = list(PAGES.keys())

page = st.sidebar.radio(
    "Navigation",
    labels,
    index=labels.index(current_label),
    key="nav_page",
)

# Keep URL query param in sync so the selection survives reloads and is
# shareable, while the browser URL always stays on the app root path.
desired_slug = PAGES[page]
if st.query_params.get("page") != desired_slug:
    st.query_params["page"] = desired_slug

if page == "Upload":
    from pages.upload import render

    render(API_URL)
elif page == "Documents":
    from pages.documents import render

    render(API_URL)
elif page == "Review Queue":
    from pages.review import render

    render(API_URL)
