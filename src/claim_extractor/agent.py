"""Claim extraction agent using LLM."""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.config import config
from src.shared.utils import load_json, save_json, ingested_from_dict
from src.shared.models import Claim
from .llm_client import LLMClient, extract_claims_from_text


@dataclass
class ExtractedClaim:
    """A claim extracted from a paper."""

    claim_id: str
    paper_id: str
    claim_type: str
    claim_text: str
    source_section: str = ""
    source_location: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "paper_id": self.paper_id,
            "claim_type": self.claim_type,
            "claim_text": self.claim_text,
            "source_section": self.source_section,
            "source_location": self.source_location,
            "confidence": self.confidence,
        }


class ClaimExtractionAgent:
    """
    Agent responsible for extracting claims from papers using LLM.

    Distinguishes between findings, hypotheses, and limitations,
    and maintains source traceability.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def extract_claims(
        self,
        papers: list[dict] | None = None,
        max_claims_per_paper: int = 20,
    ) -> list[ExtractedClaim]:
        """
        Extract claims from papers.

        Args:
            papers: List of ingested paper dicts. If None, loads from data store.
            max_claims_per_paper: Maximum claims to extract per paper

        Returns:
            List of ExtractedClaim objects
        """
        if papers is None:
            filepath = config.data_dir / config.ingested_papers_file
            data = load_json(filepath)
            papers = data

        print(f"[Agent 3] Extracting claims from {len(papers)} papers...")

        all_claims = []
        for i, paper in enumerate(papers):
            print(f"[Agent 3] Processing paper {i+1}/{len(papers)}: {paper.get('title', '')[:40]}...")

            claims = self._extract_from_paper(paper, max_claims_per_paper)
            all_claims.extend(claims)

        print(f"[Agent 3] Total claims extracted: {len(all_claims)}")
        return all_claims

    def _extract_from_paper(self, paper: dict, max_claims: int) -> list[ExtractedClaim]:
        """Extract claims from a single paper."""
        paper_id = paper.get("paper_id", "unknown")
        title = paper.get("title", "")
        full_text = paper.get("full_text", "")

        if not full_text or len(full_text) < 100:
            print(f"[Agent 3] Skipping {paper_id} - insufficient text")
            return []

        raw_claims = extract_claims_from_text(
            text=full_text,
            title=title,
            llm_client=self.llm_client,
            max_claims=max_claims,
        )

        claims = []
        for i, raw in enumerate(raw_claims):
            claim = ExtractedClaim(
                claim_id=f"{paper_id}_claim_{i+1:03d}",
                paper_id=paper_id,
                claim_type=raw.get("claim_type", "finding"),
                claim_text=raw.get("claim_text", ""),
                source_section=raw.get("source_section", ""),
                source_location=raw.get("source_location", ""),
                confidence=raw.get("confidence", 0.8),
            )
            claims.append(claim)

        return claims

    def deduplicate_claims(self, claims: list[ExtractedClaim]) -> list[ExtractedClaim]:
        """Remove duplicate or near-duplicate claims."""
        seen_texts: set[str] = set()
        unique_claims = []

        for claim in claims:
            text_lower = claim.claim_text.lower().strip()
            if text_lower and text_lower not in seen_texts:
                seen_texts.add(text_lower)
                unique_claims.append(claim)

        removed = len(claims) - len(unique_claims)
        if removed > 0:
            print(f"[Agent 3] Deduplicated {removed} claims")

        return unique_claims

    def save_claims(self, claims: list[ExtractedClaim]) -> Path:
        """Save claims to the data directory."""
        filepath = config.data_dir / config.extracted_claims_file
        data = [c.to_dict() for c in claims]
        save_json(data, filepath)
        print(f"[Agent 3] Saved {len(claims)} claims to {filepath}")
        return filepath


def main():
    """CLI entry point for Agent 3."""
    agent = ClaimExtractionAgent()
    claims = agent.extract_claims()
    claims = agent.deduplicate_claims(claims)
    agent.save_claims(claims)

    print("\n[Agent 3] Sample claims:")
    for claim in claims[:3]:
        print(f"  [{claim.claim_type.upper()}] {claim.claim_text[:60]}...")


if __name__ == "__main__":
    main()
