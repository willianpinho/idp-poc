"""Review queue page - documents flagged for human review."""

import requests
import streamlit as st


def render(api_url: str):
    st.header("Review Queue")
    st.markdown("Documents flagged for human review, sorted by confidence (lowest first).")

    resp = requests.get(f"{api_url}/api/review/queue")
    if resp.status_code != 200:
        st.error("Failed to load review queue")
        return

    data = resp.json()
    items = data.get("items", [])

    if not items:
        st.success(
            "No documents pending review. All documents have been processed with high confidence."
        )
        return

    st.metric("Pending Reviews", len(items))
    st.markdown("---")

    for item in items:
        tier = item.get("confidence_tier", "UNKNOWN")
        tier_emoji = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "❌"}.get(tier, "❓")
        confidence = item.get("overall_confidence", 0) or 0

        with st.expander(
            f"{tier_emoji} {item.get('original_filename', 'Unknown')} — {tier} ({confidence:.0%})",
            expanded=tier == "LOW",
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Category:** {item.get('category', 'N/A')}")
                category_conf = item.get("category_confidence", 0) or 0
                st.markdown(f"**Category Confidence:** {category_conf:.0%}")
                st.markdown(f"**Pages:** {item.get('page_count', 'N/A')}")
                st.markdown(f"**OCR Applied:** {'Yes' if item.get('ocr_applied') else 'No'}")

                if item.get("ocr_applied") and item.get("ocr_confidence"):
                    st.markdown(f"**OCR Confidence:** {item['ocr_confidence']:.0%}")

            with col2:
                st.markdown(f"**Title:** {item.get('title') or 'N/A'}")
                if item.get("summary"):
                    st.markdown(f"**Summary:** {item['summary'][:200]}...")
                duration = item.get("processing_duration_ms", 0) or 0
                st.markdown(f"**Processing Time:** {duration:,} ms")

            # Review actions
            st.markdown("---")
            analysis_id = str(item.get("analysis_id", ""))

            review_notes = st.text_area(
                "Review Notes",
                value=item.get("review_notes") or "",
                key=f"notes_{analysis_id}",
                placeholder="Add review notes here...",
            )

            col_approve, col_save = st.columns(2)

            with col_approve:
                if st.button("Approve & Complete", key=f"approve_{analysis_id}", type="primary"):
                    resp = requests.patch(
                        f"{api_url}/api/review/{analysis_id}",
                        json={"review_notes": review_notes, "approved": True},
                    )
                    if resp.status_code == 200:
                        st.success("Document approved!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {resp.text}")

            with col_save:
                if st.button("Save Notes", key=f"save_{analysis_id}"):
                    resp = requests.patch(
                        f"{api_url}/api/review/{analysis_id}",
                        json={"review_notes": review_notes, "approved": False},
                    )
                    if resp.status_code == 200:
                        st.success("Notes saved")
                    else:
                        st.error(f"Failed: {resp.text}")
