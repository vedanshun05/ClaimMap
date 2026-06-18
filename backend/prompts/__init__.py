"""Prompts package."""

from .claim_extraction import (
    get_claim_extraction_prompt,
    get_strict_claim_extraction_prompt,
    CLAIM_EXTRACTION_SYSTEM_PROMPT,
    CLAIM_EXTRACTION_STRICT_SYSTEM_PROMPT,
    MAX_CHARS_PER_SECTION,
)
from .relation_detection import (
    get_relation_detection_prompt,
    get_brief_generation_prompt,
    RELATION_DETECTION_SYSTEM_PROMPT,
    BRIEF_GENERATION_SYSTEM_PROMPT
)

__all__ = [
    "get_claim_extraction_prompt",
    "get_strict_claim_extraction_prompt",
    "CLAIM_EXTRACTION_SYSTEM_PROMPT",
    "CLAIM_EXTRACTION_STRICT_SYSTEM_PROMPT",
    "MAX_CHARS_PER_SECTION",
    "get_relation_detection_prompt",
    "get_brief_generation_prompt",
    "RELATION_DETECTION_SYSTEM_PROMPT",
    "BRIEF_GENERATION_SYSTEM_PROMPT",
]