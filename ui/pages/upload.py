"""Upload page - drag-and-drop PDF upload with processing trigger."""

import requests
import streamlit as st


def render(api_url: str):
    st.header("Upload Document")
    st.markdown("Upload a PDF document to analyze with the IDP pipeline.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF document for intelligent processing",
    )

    if uploaded_file is not None:
        st.info(f"**File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Upload & Process", type="primary", use_container_width=True):
                with st.spinner("Uploading document..."):
                    # Upload
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }
                    resp = requests.post(f"{api_url}/api/documents", files=files)

                    if resp.status_code != 201:
                        st.error(f"Upload failed: {resp.text}")
                        return

                    doc = resp.json()
                    doc_id = doc["id"]
                    st.success(f"Document uploaded: `{doc_id}`")

                with st.spinner("Running IDP pipeline (this may take a minute)..."):
                    # Process
                    proc_resp = requests.post(f"{api_url}/api/documents/{doc_id}/process")

                    if proc_resp.status_code != 200:
                        st.error(f"Processing failed: {proc_resp.text}")
                        return

                    result = proc_resp.json()

                st.success("Processing complete!")

                # Show results summary
                tier = result.get("confidence_tier", "UNKNOWN")
                tier_color = {"HIGH": "green", "MEDIUM": "orange", "LOW": "red"}.get(tier, "gray")

                st.markdown(f"""
                ### Results Summary

                | Field | Value |
                |-------|-------|
                | **Status** | {result.get("status")} |
                | **Category** | {result.get("category", "N/A")} |
                | **Confidence Tier** | :{tier_color}[**{tier}**] |
                | **Overall Confidence** | {result.get("overall_confidence", 0):.2%} |
                | **Tokens Used** | {result.get("tokens_used", 0):,} |
                """)

                if result.get("summary"):
                    st.markdown(f"**Summary:** {result['summary']}")

                st.markdown("---")
                st.markdown("Go to **Documents** page to see full details and chat.")

        with col2:
            if st.button("Upload Only", use_container_width=True):
                with st.spinner("Uploading..."):
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }
                    resp = requests.post(f"{api_url}/api/documents", files=files)
                    if resp.status_code == 201:
                        st.success(f"Uploaded: `{resp.json()['id']}`")
                    else:
                        st.error(f"Failed: {resp.text}")
