"""
shared/llm/client.py
────────────────────
Unified LLM client via LiteLLM.
OpenAI-only configuration — cost-optimised model tiers per agent type.

Model assignment rationale (cheapest model that can handle the task):
  cheap     → gpt-4o-mini  : intent classification, RAG synthesis, market, soil
  fast      → gpt-4o-mini  : same as cheap; alias kept for code clarity
  reasoning → gpt-4o       : complex multi-step reasoning (disease, fertilizer)
  vision    → gpt-4o       : image analysis (requires vision capability)
  local     → gpt-4o-mini  : fallback alias when no local model available
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# ── Load .env before os.getenv is called ─────────────────────────────────────
try:
    from dotenv import load_dotenv
    _base = os.path.join(os.path.dirname(__file__), "..", "..")
    load_dotenv(dotenv_path=os.path.join(_base, ".env"), override=False)
    load_dotenv(dotenv_path=os.path.join(_base, ".env.local"), override=True)
except ImportError:
    pass  # rely on shell / Docker env

try:
    import litellm
    from litellm import acompletion
    litellm.set_verbose = False

    # Propagate OpenAI key so LiteLLM always finds it
    _openai_key = os.getenv("OPENAI_API_KEY", "")
    if _openai_key:
        litellm.openai_key = _openai_key
        os.environ["OPENAI_API_KEY"] = _openai_key

    LITELLM_AVAILABLE = bool(_openai_key)
    if not LITELLM_AVAILABLE:
        import warnings
        warnings.warn(
            "OPENAI_API_KEY is not set. All LLM calls will use the mock fallback. "
            "Add OPENAI_API_KEY=sk-... to your .env file.",
            RuntimeWarning,
            stacklevel=1,
        )
except ImportError:
    LITELLM_AVAILABLE = False
    acompletion = None  # type: ignore

from shared.utils.logging import get_logger

logger = get_logger(__name__)

# ── Model tiers ────────────────────────────────────────────────────────────────
# All aliases resolve to OpenAI models. Override via .env if needed.
#
#  cheap / fast  →  gpt-4o-mini   (~$0.15/1M in, $0.60/1M out)
#  reasoning     →  gpt-4o        (~$2.50/1M in, $10/1M out) — use sparingly
#  vision        →  gpt-4o        (only model with vision support)
#  local         →  gpt-4o-mini   (fallback; set LOCAL_LLM=ollama/llama3 if you
#                                   run a local server)
MODEL_MAP = {
    "cheap":     os.getenv("DEFAULT_LLM",   "openai/gpt-4o-mini"),
    "fast":      os.getenv("FAST_LLM",      "openai/gpt-4o-mini"),   # was groq — now OpenAI
    "reasoning": os.getenv("REASONING_LLM", "openai/gpt-4o"),
    "vision":    os.getenv("VISION_LLM",    "openai/gpt-4o"),
    "local":     os.getenv("LOCAL_LLM",     "openai/gpt-4o-mini"),
}

# Per-agent model alias — edit here to tune cost vs quality per agent
AGENT_MODEL: Dict[str, str] = {
    # Intent classification: fast + cheap — runs on every request
    "intent_classifier":        "fast",
    # RAG synthesis: cheap — retrieval does the heavy lifting
    "rag_knowledge_agent":      "cheap",
    # Crop planning: cheap — structured JSON output, deterministic
    "crop_planning_agent":      "cheap",
    # Market agent: cheap — mostly formatting price data
    "market_agent":             "cheap",
    # Weather agent: cheap — weather API provides the data, LLM just formats
    "weather_agent":            "cheap",
    # Soil agent: cheap — guideline-based recommendations
    "soil_agent":               "cheap",
    # Fertilizer: reasoning — requires multi-factor agronomic reasoning
    "fertilizer_agent":         "reasoning",
    # Disease detection: reasoning — needs nuanced pathology analysis
    "disease_detection":        "reasoning",
    # Image analysis: vision — requires multimodal model
    "image_analysis":           "vision",
    # Synthesis / orchestrator: cheap — just formatting already-processed data
    "synthesis":                "cheap",
}

SYSTEM_PROMPT_BASE = """You are KrishiMind, an expert agricultural AI assistant.
You help farmers across India and globally with crop management, disease detection,
soil health, market intelligence, and sustainable farming.
Always be practical, empathetic, and farmer-friendly.
Use simple language, avoid jargon, and provide step-by-step guidance.
Include confidence levels and warnings where appropriate.
When uncertain, ask clarifying questions rather than guessing."""


def _mock_response(prompt: str, _system: str) -> str:
    return (
        "⚠️ LLM not configured. Add OPENAI_API_KEY=sk-... to your .env file.\n\n"
        f"Your query was: {prompt[:120]}..."
    )


async def chat_completion(
    messages: List[Dict[str, str]],
    model_alias: str = "cheap",
    temperature: float = 0.3,
    max_tokens: int = 1024,
    system_override: Optional[str] = None,
) -> str:
    """Async chat completion with automatic cheap-model fallback.

    Args:
        messages:        List of {role, content} dicts (NO system message — added here).
        model_alias:     Key from MODEL_MAP: cheap | fast | reasoning | vision | local.
        temperature:     Sampling temperature (0.1 = deterministic, 0.7 = creative).
        max_tokens:      Max tokens in the response.
        system_override: Replace the default KrishiMind system prompt.

    Returns:
        Response text string. Never raises — returns a user-facing error string on failure.
    """
    model = MODEL_MAP.get(model_alias, MODEL_MAP["cheap"])
    system = system_override or SYSTEM_PROMPT_BASE

    if not LITELLM_AVAILABLE:
        logger.warning("LiteLLM unavailable / no API key — returning mock response")
        return _mock_response(messages[-1].get("content", ""), system)

    full_messages = [{"role": "system", "content": system}] + messages

    try:
        response = await acompletion(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    except Exception as primary_err:
        logger.warning(
            "Primary model %s failed: %s — trying fallback",
            model, primary_err,
        )
        # Always fall back to the cheapest OpenAI model
        fallback = MODEL_MAP["cheap"]
        if fallback == model:
            # Already on the cheapest — nothing to fall back to
            logger.error("Fallback model same as primary; giving up: %s", primary_err)
            return (
                "I encountered a technical issue. Please try again or contact support."
            )
        try:
            response = await acompletion(
                model=fallback,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as fallback_err:
            logger.error("Fallback model %s also failed: %s", fallback, fallback_err)
            return (
                "I encountered a technical issue. Please try again or contact support."
            )


async def vision_completion(
    messages: Optional[List[Dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1500,
    text_prompt: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
) -> str:
    """Vision-enabled completion for image analysis (requires gpt-4o).

    Two calling styles:
      1. vision_completion(messages=[...], system_prompt="...")
      2. vision_completion(text_prompt="...", image_urls=[...])   ← legacy
    """
    system = system_prompt or SYSTEM_PROMPT_BASE
    model = MODEL_MAP["vision"]  # always gpt-4o

    if not LITELLM_AVAILABLE:
        return _mock_response(text_prompt or "image analysis", system)

    if messages is not None:
        full_messages = [{"role": "system", "content": system}] + messages
    else:
        content: List[Any] = [{"type": "text", "text": text_prompt or ""}]
        for url in (image_urls or []):
            content.append({"type": "image_url", "image_url": {"url": url, "detail": "high"}})
        full_messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": content},
        ]

    try:
        response = await acompletion(
            model=model,
            messages=full_messages,
            temperature=0.2,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.error("Vision completion failed: %s", exc)
        return "Unable to analyse the image at this time. Please try again."


# ── LLMClient class wrapper ───────────────────────────────────────────────────

class LLMClient:
    """Thin object wrapper so agents can do:
        _llm = LLMClient()
        await _llm.chat_completion(...)
    """

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model_alias: str = "cheap",
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        return await chat_completion(
            messages=messages,
            model_alias=model_alias,
            temperature=temperature,
            max_tokens=max_tokens,
            system_override=system_prompt,
        )

    async def vision_completion(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        text_prompt: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
    ) -> str:
        return await vision_completion(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            text_prompt=text_prompt,
            image_urls=image_urls,
        )