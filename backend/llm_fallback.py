"""Shared LLM fallback: try OpenCode Zen, then NVIDIA NIM, then Gemini."""

import os
import logging

logger = logging.getLogger(__name__)

OPENCODE_BASE = "https://opencode.ai/zen/v1"
NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
GEMINI_BASE = None


def get_llm_config():
    """Return (model, api_base, api_key) for the first available backend."""
    opencode_key = os.getenv("OPENCODE_API_KEY")
    if opencode_key:
        model = os.getenv("DEFAULT_MODEL", "openai/deepseek-v4-flash-free")
        logger.info("[LLM] Using OpenCode Zen backend")
        return model, OPENCODE_BASE, opencode_key

    nvidia_key = os.getenv("NVIDIA_NIM_API_KEY")
    if nvidia_key:
        model = os.getenv("DEFAULT_MODEL", "nvidia_nim/meta/llama-3.1-8b-instruct")
        logger.info("[LLM] Falling back to NVIDIA NIM backend")
        os.environ["NVIDIA_API_KEY"] = nvidia_key
        return model, NVIDIA_BASE, nvidia_key

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        model = os.getenv("DEFAULT_MODEL", "gemini/gemini-2.0-flash-exp")
        logger.info("[LLM] Falling back to Gemini backend")
        return model, None, gemini_key

    logger.warning("[LLM] No API keys found — LLM calls will fail")
    return os.getenv("DEFAULT_MODEL", "openai/deepseek-v4-flash-free"), OPENCODE_BASE, None
