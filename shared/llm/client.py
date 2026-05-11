"""
shared/llm/client.py
────────────────────
Unified LLM client via LiteLLM.
Handles model routing, retries, and fallbacks.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    import litellm
    from litellm import completion, acompletion
    litellm.set_verbose = False
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from shared.utils.logging import get_logger

logger = get_logger(__name__)

# ── Model aliases ─────────────────────────────────────────────────────────────
MODEL_MAP = {
    "cheap":      os.getenv("DEFAULT_LLM", "openai/gpt-4o-mini"),
    "reasoning":  os.getenv("REASONING_LLM", "anthropic/claude-3-5-sonnet-20241022"),
    "vision":     os.getenv("VISION_LLM", "openai/gpt-4o"),
    "local":      os.getenv("LOCAL_LLM", "ollama/llama3"),
    "fast":       os.getenv("FAST_LLM", "groq/llama-3.1-8b-instant"),
}

SYSTEM_PROMPT_BASE = """You are KrishiMind, an expert agricultural AI assistant.
You help farmers across India and globally with crop management, disease detection,
soil health, market intelligence, and sustainable farming.
Always be practical, empathetic, and farmer-friendly.
Use simple language, avoid jargon, and provide step-by-step guidance.
Include confidence levels and warnings where appropriate.
When uncertain, ask clarifying questions rather than guessing."""


def _mock_response(prompt: str, system: str) -> str:
    """Fallback when LiteLLM is not available (dev without API keys)."""
    return (
        "⚠️ LLM not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env.local\n\n"
        f"Your query was: {prompt[:100]}..."
    )


async def chat_completion(
    messages: List[Dict[str, str]],
    model_alias: str = "cheap",
    temperature: float = 0.3,
    max_tokens: int = 1024,
    system_override: Optional[str] = None,
) -> str:
    """
    Async chat completion with automatic fallback.
    
    Args:
        messages: List of {role, content} dicts
        model_alias: One of cheap | reasoning | vision | local | fast
        temperature: Sampling temperature
        max_tokens: Maximum response tokens
        system_override: Override the default system prompt
    
    Returns:
        Response text string
    """
    model = MODEL_MAP.get(model_alias, MODEL_MAP["cheap"])
    system = system_override or SYSTEM_PROMPT_BASE

    if not LITELLM_AVAILABLE:
        logger.warning("LiteLLM not available, using mock response")
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
    except Exception as e:
        logger.warning("Primary model %s failed: %s — trying fallback", model, e)
        # Try cheap fallback
        try:
            fallback = MODEL_MAP["cheap"]
            if fallback != model:
                response = await acompletion(
                    model=fallback,
                    messages=full_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
        except Exception as e2:
            logger.error("Fallback also failed: %s", e2)

        return (
            "I encountered a technical issue connecting to my knowledge system. "
            "Please try again or contact support if the problem persists."
        )


async def vision_completion(
    messages: Optional[List[Dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1500,
    # Legacy positional-style args kept for backwards compat
    text_prompt: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
) -> str:
    """Vision-enabled completion for image analysis.

    Supports two calling styles:
      1. vision_completion(messages=[...], system_prompt="...")   ← used by image_analysis/service.py
      2. vision_completion(text_prompt="...", image_urls=[...])   ← legacy
    """
    system = system_prompt or SYSTEM_PROMPT_BASE
    model = MODEL_MAP["vision"]

    if not LITELLM_AVAILABLE:
        return _mock_response(text_prompt or "", system)

    # Build message list
    if messages is not None:
        full_messages = [{"role": "system", "content": system}] + messages
    else:
        content: List[Any] = [{"type": "text", "text": text_prompt or ""}]
        for url in (image_urls or []):
            content.append({"type": "image_url", "image_url": {"url": url, "detail": "high"}})
        full_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ]

    try:
        response = await acompletion(
            model=model,
            messages=full_messages,
            temperature=0.2,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error("Vision completion failed: %s", e)
        return "Unable to analyze image at this time. Please try again."


# ── LLMClient class ────────────────────────────────────────────────────────────
# Thin wrapper so files can do:  _llm = LLMClient()  then  await _llm.chat_completion(...)

class LLMClient:
    """Class-based wrapper around the module-level async functions.

    Lets agent files import and instantiate a client object while the
    actual logic lives in the standalone functions above.
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