"""Documents page - list, detail view, and chat."""

import requests
import streamlit as st


def render(api_url: str):
    st.header("Documents")

    # Fetch documents
    resp = requests.get(f"{api_url}/api/documents")
    if resp.status_code != 200:
        st.error("Failed to load documents")
        return

    data = resp.json()
    docs = data.get("documents", [])

    if not docs:
        st.info("No documents uploaded yet. Go to **Upload** to add one.")
        return

    # Document selector
    doc_options = {f"{d['original_filename']} ({d['status']})": d["id"] for d in docs}
    selected = st.selectbox("Select a document", list(doc_options.keys()))
    doc_id = doc_options[selected]

    # Show document detail
    _render_detail(api_url, doc_id)

    st.markdown("---")

    # Chat section
    _render_chat(api_url, doc_id)


def _render_detail(api_url: str, doc_id: str):
    """Render document analysis details."""
    # Get document info
    doc_resp = requests.get(f"{api_url}/api/documents/{doc_id}")
    if doc_resp.status_code != 200:
        st.error("Failed to load document")
        return

    doc = doc_resp.json()

    # Basic info
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", doc["status"])
    col2.metric("Pages", doc.get("page_count") or "N/A")
    col3.metric("Size", f"{doc['file_size_bytes'] / 1024:.1f} KB")

    # Try to get analysis
    analysis_resp = requests.get(f"{api_url}/api/documents/{doc_id}/analysis")
    if analysis_resp.status_code != 200:
        if doc["status"] == "uploaded":
            if st.button("Process Document", type="primary"):
                with st.spinner("Processing..."):
                    proc = requests.post(f"{api_url}/api/documents/{doc_id}/process")
                    if proc.status_code == 200:
                        st.success("Done! Refresh page to see results.")
                        st.rerun()
                    else:
                        st.error(f"Failed: {proc.text}")
        return

    analysis = analysis_resp.json()

    # Confidence tier badge
    tier = analysis.get("confidence_tier", "UNKNOWN")
    tier_emoji = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "❌"}.get(tier, "❓")

    confidence_pct = analysis.get("overall_confidence", 0)
    st.markdown(f"### {tier_emoji} Confidence: **{tier}** ({confidence_pct:.2%})")

    # Classification & Extraction
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Classification")
        st.markdown(f"**Category:** {analysis.get('category', 'N/A')}")
        st.markdown(f"**Confidence:** {analysis.get('category_confidence', 0):.2%}")

        st.markdown("#### Metadata")
        st.markdown(f"**Title:** {analysis.get('title') or 'N/A'}")
        st.markdown(f"**Author:** {analysis.get('author') or 'N/A'}")
        st.markdown(f"**Date:** {analysis.get('document_date') or 'N/A'}")
        st.markdown(f"**Language:** {analysis.get('language') or 'N/A'}")

    with col2:
        st.markdown("#### Quality Assessment")
        quality_metrics = {
            "Overall": analysis.get("quality_score", 0),
            "Readability": analysis.get("readability_score", 0),
            "Completeness": analysis.get("completeness_score", 0),
            "Structure": analysis.get("structure_score", 0),
        }
        for name, score in quality_metrics.items():
            if score:
                st.progress(score, text=f"{name}: {score:.0%}")

        st.markdown("#### Processing")
        st.markdown(f"**Duration:** {analysis.get('processing_duration_ms', 0):,} ms")
        st.markdown(f"**Tokens:** {analysis.get('llm_tokens_used', 0):,}")
        st.markdown(f"**OCR Applied:** {'Yes' if analysis.get('ocr_applied') else 'No'}")

    # Summary
    if analysis.get("summary"):
        st.markdown("#### Summary")
        st.markdown(analysis["summary"])

    # Entities
    entities = analysis.get("key_entities", [])
    if entities:
        st.markdown("#### Key Entities")
        entity_data = [
            {"Name": e["name"], "Type": e["type"], "Confidence": f"{e['confidence']:.0%}"}
            for e in entities
        ]
        st.dataframe(entity_data, use_container_width=True)

    # Key Terms
    terms = analysis.get("key_terms", [])
    if terms:
        st.markdown("#### Key Terms")
        st.markdown(" | ".join(f"`{t}`" for t in terms))

    # Download link
    dl_resp = requests.get(f"{api_url}/api/documents/{doc_id}/download")
    if dl_resp.status_code == 200:
        st.markdown(f"[Download Original PDF]({dl_resp.json()['download_url']})")


def _render_chat(api_url: str, doc_id: str):
    """Render chat Q&A section."""
    st.markdown("### 💬 Ask about this document")

    # Show chat history
    history_resp = requests.get(f"{api_url}/api/documents/{doc_id}/chat/history")
    if history_resp.status_code == 200:
        messages = history_resp.json()
        for msg in messages:
            role = msg["role"]
            icon = "🧑" if role == "user" else "🤖"
            st.markdown(f"**{icon} {role.title()}:** {msg['content']}")

            # Show sources for assistant messages
            sources = msg.get("sources", [])
            if sources and role == "assistant":
                with st.expander("Sources"):
                    for s in sources:
                        pages = ", ".join(str(p) for p in s.get("page_numbers", []))
                        st.markdown(
                            f"- **Pages {pages}** (relevance: {s.get('relevance_score', 0):.2%}): "
                            f"{s.get('snippet', '')[:150]}..."
                        )

    # Input
    question = st.text_area(
        "Your question",
        placeholder="What is this document about?",
        key=f"chat_{doc_id}",
    )

    if st.button("Ask", type="primary") and question:
        with st.spinner("Searching document and generating answer..."):
            resp = requests.post(
                f"{api_url}/api/documents/{doc_id}/chat",
                json={"question": question},
            )
            if resp.status_code == 200:
                result = resp.json()
                st.markdown(f"**🤖 Answer:** {result['answer']}")
                st.markdown(f"*Confidence: {result.get('confidence', 'N/A')}*")

                if result.get("sources"):
                    with st.expander("Sources"):
                        for s in result["sources"]:
                            pages = ", ".join(str(p) for p in s.get("page_numbers", []))
                            relevance = s.get("relevance_score", 0)
                            st.markdown(f"- **Pages {pages}** (relevance: {relevance:.2%})")
            else:
                st.error(f"Failed: {resp.text}")
