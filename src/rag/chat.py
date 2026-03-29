"""RAG-powered conversational Q&A over documents."""

import json
import logging

import anthropic

from src.config import settings
from src.models.schemas import ChatResponse, ChatSource
from src.rag.retriever import search_similar_chunks
from src.storage import database as db

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are PraxisIQ, a document analysis assistant.
Your role is to answer questions about a specific document based ONLY on
the provided context chunks.

Rules:
1. Answer ONLY based on the provided document context. Do not use external knowledge.
2. If the answer is not in the context, say: "I cannot find this in the document."
3. Always cite the page number(s) where you found the information using [Page X] format.
4. Be concise and precise in your answers.
5. If the context is ambiguous, explain what the document says and note the ambiguity.

Your response must be in the same language as the question."""

QUERY_PROMPT = """Document Context:
---
{context}
---

Chat History:
{history}

User Question: {question}

Answer the question based on the document context above. Cite page numbers."""


async def ask_question(
    document_id: str,
    question: str,
    include_history: bool = True,
) -> ChatResponse:
    """Ask a question about a document using RAG.

    1. Retrieve relevant chunks via vector similarity search
    2. Build context from retrieved chunks
    3. Send to Claude with system prompt and chat history
    4. Store messages and return response

    Args:
        document_id: UUID of the document.
        question: User's question.
        include_history: Whether to include chat history for context.

    Returns:
        ChatResponse with answer, sources, and confidence.
    """
    # Retrieve relevant chunks
    chunks = await search_similar_chunks(document_id, question, top_k=5)

    if not chunks:
        return ChatResponse(
            answer="No content found for this document. "
            "Please ensure the document has been processed.",
            sources=[],
            confidence="low",
        )

    # Build context from chunks
    context_parts = []
    sources = []
    for chunk in chunks:
        pages_str = ", ".join(str(p + 1) for p in chunk.page_numbers)
        context_parts.append(f"[Pages {pages_str}]:\n{chunk.content}")
        sources.append(
            ChatSource(
                chunk_id=chunk.chunk_id,
                page_numbers=[p + 1 for p in chunk.page_numbers],
                relevance_score=chunk.relevance_score,
                snippet=chunk.content[:200],
            )
        )

    context = "\n\n---\n\n".join(context_parts)

    # Get chat history
    history = ""
    if include_history:
        history_rows = await db.fetch(
            """SELECT role, content FROM chat_messages
               WHERE document_id = $1
               ORDER BY created_at DESC LIMIT 6""",
            document_id,
        )
        if history_rows:
            history_parts = []
            for row in reversed(history_rows):
                history_parts.append(f"{row['role']}: {row['content'][:300]}")
            history = "\n".join(history_parts)

    # Build prompt
    prompt = QUERY_PROMPT.format(
        context=context,
        history=history or "(no previous conversation)",
        question=question,
    )

    # Call Claude
    if not settings.anthropic_api_key:
        answer = (
            "API key not configured. In production, this would use Claude "
            "to answer based on the retrieved context."
        )
        confidence = "low"
    else:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.content[0].text
        # Estimate confidence based on retrieval scores
        avg_relevance = sum(c.relevance_score for c in sources) / len(sources)
        confidence = "high" if avg_relevance > 0.8 else "medium" if avg_relevance > 0.5 else "low"

    # Save messages to history
    await db.execute(
        """INSERT INTO chat_messages (document_id, role, content, sources)
           VALUES ($1, 'user', $2, '[]')""",
        document_id,
        question,
    )
    await db.execute(
        """INSERT INTO chat_messages (document_id, role, content, sources)
           VALUES ($1, 'assistant', $2, $3)""",
        document_id,
        answer,
        json.dumps([s.model_dump() for s in sources]),
    )

    return ChatResponse(answer=answer, sources=sources, confidence=confidence)
