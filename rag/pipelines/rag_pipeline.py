"""RAG (Retrieval-Augmented Generation) pipeline for agricultural knowledge.

Architecture:
  1. Embed the user query.
  2. Retrieve top-k relevant chunks from Qdrant (vector DB).
  3. Optionally retrieve structured data from PostgreSQL.
  4. Synthesise an answer using the LLM with retrieved context.

Falls back to pure LLM generation when Qdrant is unavailable.
"""

import json
import os
import re
from typing import List, Optional, Dict, Any

from shared.llm.client import LLMClient
from shared.utils.logging import get_logger

logger = get_logger("rag.pipeline")
_llm = LLMClient()

_QDRANT_URL     = os.getenv("QDRANT_URL", "http://localhost:6333")
_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
_KB_COLLECTION  = "krishimind_knowledge_base"
_EMBED_DIM      = 1536

try:
    from qdrant_client import AsyncQdrantClient
    _qdrant = AsyncQdrantClient(url=_QDRANT_URL, api_key=_QDRANT_API_KEY or None)
    _use_qdrant = True
except Exception:
    _qdrant = None  # type: ignore
    _use_qdrant = False


RAG_SYSTEM_PROMPT = """You are KrishiMind-AI, an expert agricultural advisor for Indian farmers.
Answer the farmer's question using ONLY the retrieved context below.
If the context doesn't contain the answer, say so honestly and provide general guidance.

Guidelines:
- Be practical and specific to Indian farming conditions.
- Reference government schemes (PM-KISAN, PMFBY, KCC, eNAM, etc.) where relevant.
- Use simple language suitable for farmers with varying literacy levels.
- Provide actionable steps the farmer can take today.
- Mention local resources (KVK, ATMA, state agriculture departments) when helpful.
- If recommending inputs, prefer locally available products and bio-alternatives.

Retrieved Knowledge Context:
{context}"""

# ── Embedding helper (shared with vector_memory) ─────────────────────────────

async def _embed(text: str) -> List[float]:
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        resp = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding
    except Exception:
        import random, math
        rng = random.Random(hash(text))
        return [rng.gauss(0, 1) for _ in range(_EMBED_DIM)]


# ── Retrieval ────────────────────────────────────────────────────────────────

async def _retrieve_chunks(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve the most relevant knowledge base chunks for the query."""
    if not _use_qdrant:
        return []

    query_vec = await _embed(query)
    try:
        results = await _qdrant.search(
            collection_name=_KB_COLLECTION,
            query_vector=query_vec,
            limit=top_k,
            with_payload=True,
        )
        return [
            {
                "text": r.payload.get("text", ""),
                "source": r.payload.get("source", "KrishiMind KB"),
                "score": r.score,
            }
            for r in results
            if r.score > 0.65  # relevance threshold
        ]
    except Exception as exc:
        logger.warning("qdrant_retrieval_error", extra={"error": str(exc)})
        return []


def _format_context(chunks: List[Dict]) -> str:
    if not chunks:
        return "No specific knowledge base entries found for this query."
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


# ── Main public function ─────────────────────────────────────────────────────

async def rag_answer(
    query: str,
    farm_context: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Generate a RAG-augmented answer to an agricultural query.

    Returns:
        {
          "answer": str,
          "sources": [{"source": str, "relevance_score": float}, ...],
          "retrieved_chunks": int,
          "used_rag": bool,
        }
    """
    farm_ctx = farm_context or {}

    # 1. Retrieve
    chunks = await _retrieve_chunks(query, top_k=top_k)
    context_text = _format_context(chunks)

    # 2. Build messages
    messages = []
    if history:
        for turn in history[-4:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

    # Enrich query with farm context
    enriched_query = query
    if farm_ctx.get("location"):
        enriched_query += f"\n\n[Farmer location: {farm_ctx['location']}]"
    if farm_ctx.get("primary_crops"):
        enriched_query += f"\n[Primary crops: {', '.join(farm_ctx['primary_crops'])}]"

    messages.append({"role": "user", "content": enriched_query})

    # 3. Generate
    system = RAG_SYSTEM_PROMPT.format(context=context_text)

    try:
        answer = await _llm.chat_completion(
            messages=messages,
            system_prompt=system,
            model_alias="cheap",
            temperature=0.3,
            max_tokens=800,
        )

        logger.info(
            "rag_answer_generated",
            extra={
                "chunks_retrieved": len(chunks),
                "used_rag": bool(chunks),
                "query_len": len(query),
            },
        )

        return {
            "answer": answer,
            "sources": [{"source": c["source"], "relevance_score": round(c.get("score", 0), 3)} for c in chunks],
            "retrieved_chunks": len(chunks),
            "used_rag": bool(chunks),
        }

    except Exception as exc:
        logger.error("rag_generation_error", extra={"error": str(exc)})
        return {
            "answer": (
                "I'm having trouble accessing the knowledge base right now. "
                "Please consult your local Krishi Vigyan Kendra (KVK) or call "
                "the Kisan Call Centre at 1800-180-1551 for immediate help."
            ),
            "sources": [],
            "retrieved_chunks": 0,
            "used_rag": False,
        }
