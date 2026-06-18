"""Claim validator - validates claims against source text."""

import re
from typing import Optional


class ClaimValidator:
    """Validates that claims exist verbatim in source text."""

    def __init__(self, match_threshold: float = 0.90):
        """
        Initialize claim validator.

        Args:
            match_threshold: Minimum substring match ratio to consider valid (0.0-1.0)
        """
        self.match_threshold = match_threshold

    def validate(self, claim: dict, source_text: str) -> bool:
        """
        Validate that a claim's source sentence exists in the source text.

        Args:
            claim: Claim dictionary with 'source_sentence' field
            source_text: The full source text to validate against

        Returns:
            True if the source sentence is found in the source text
        """
        source_sentence = claim.get("source_sentence", "")

        if not source_sentence:
            return False

        normalized_sentence = self._normalize_text(source_sentence)
        normalized_text = self._normalize_text(source_text)

        if normalized_sentence in normalized_text:
            return True

        if self._calculate_match_ratio(normalized_sentence, normalized_text) >= self.match_threshold:
            return True

        return False

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def _calculate_match_ratio(self, sentence: str, text: str) -> float:
        """
        Calculate how much of the sentence appears in the text.

        Returns a ratio from 0.0 to 1.0.
        """
        if not sentence or not text:
            return 0.0

        words = sentence.split()
        if not words:
            return 0.0

        matched_words = 0
        for word in words:
            if word in text:
                matched_words += 1

        return matched_words / len(words)

    def filter_valid(self, claims: list[dict], source_sections: dict[str, str]) -> tuple[list[dict], list[dict]]:
        """
        Filter claims to only those that are valid.

        Args:
            claims: List of claim dictionaries
            source_sections: Dict mapping section name to section content

        Returns:
            Tuple of (valid_claims, invalid_claims)
        """
        valid_claims = []
        invalid_claims = []

        for claim in claims:
            section_name = claim.get("source_section", "")
            source_text = source_sections.get(section_name, "")

            if self.validate(claim, source_text):
                claim["is_validated"] = True
                valid_claims.append(claim)
            else:
                claim["is_validated"] = False
                invalid_claims.append(claim)

        return valid_claims, invalid_claims


validator = ClaimValidator()
