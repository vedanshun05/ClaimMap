"""Claim Extractor module - LLM-powered claim extraction from papers."""

from .llm_client import LLMClient, ClaimExtractionPrompt, extract_claims_from_text
from .agent import ClaimExtractionAgent, ExtractedClaim

__all__ = [
    "LLMClient",
    "ClaimExtractionPrompt",
    "extract_claims_from_text",
    "ClaimExtractionAgent",
    "ExtractedClaim",
]
