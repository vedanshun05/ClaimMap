"""Shared LLM client using OpenAI SDK (direct OpenAI API).

This module centralizes how we talk to the LLM so that the rest of the
codebase doesn't care about provider-specific details.

We look for an API key in the following env vars (in order):
- ``OPENAI_API_KEY``  (standard OpenAI SDK)
- ``OPENCODE_API_KEY`` (backwards-compatible name from earlier setup)

The default model is read from ``DEFAULT_MODEL`` and falls back to
``gpt-4.1-mini`` if unset.
"""

import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_api_key() -> str | None:
    """Return the configured API key, if any.

    We support both ``OPENAI_API_KEY`` and ``OPENCODE_API_KEY`` for
    backwards compatibility.
    """

    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENCODE_API_KEY")


def get_client() -> AsyncOpenAI:
    """Get or create the shared AsyncOpenAI client for OpenAI."""
    global _client
    if _client is None:
        api_key = _get_api_key()
        if not api_key:
            logger.warning("OPENAI_API_KEY/OPENCODE_API_KEY not set — LLM calls will fail")
        _client = AsyncOpenAI(api_key=api_key or "dummy")
    return _client


async def llm_completion(
    messages: list,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
    timeout: float = 30.0,
) -> str:
    """Make an LLM completion call via OpenCode Zen and return the response text.

    Args:
        messages: List of message dicts with role/content keys.
        model: Model name (defaults to DEFAULT_MODEL env or deepseek-v4-flash-free).
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in the response.
        timeout: Request timeout in seconds.

    Returns:
        The response text content.

    Raises:
        Exception: Upstream API errors propagate to the caller.
    """
    model = model or os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
    client = get_client()

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    return response.choices[0].message.content
