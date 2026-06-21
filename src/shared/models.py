"""Data models for the research synthesis pipeline."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaperMetadata:
    """Basic paper metadata."""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    source: str  # "arxiv" or "semantic_scholar"
    relevance_score: float = 0.0
    citation_count: int = 0
    year: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "citation_count": self.citation_count,
            "year": self.year,
        }


@dataclass
class IngestedPaper:
    """Paper with extracted structured fields."""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str = ""
    methodology: str = ""
    key_findings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    conclusion: str = ""
    full_text: str = ""
    pages: int = 0
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "methodology": self.methodology,
            "key_findings": self.key_findings,
            "limitations": self.limitations,
            "conclusion": self.conclusion,
            "full_text": self.full_text,
            "pages": self.pages,
            "source": self.source,
        }


@dataclass
class Claim:
    """Extracted claim with provenance."""

    claim_id: str
    paper_id: str
    claim_type: str  # "finding", "hypothesis", "limitation"
    claim_text: str
    source_section: str = ""
    source_location: str = ""  # e.g., "page 5, paragraph 2"
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


@dataclass
class ThemeSynthesis:
    """Synthesis for a single theme."""

    theme_id: str
    theme_name: str
    claim_ids: list[str]
    consensus: str  # "strong", "moderate", "weak", "conflicting"
    agreement_count: int = 0
    conflict_count: int = 0
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme_id": self.theme_id,
            "theme_name": self.theme_name,
            "claim_ids": self.claim_ids,
            "consensus": self.consensus,
            "agreement_count": self.agreement_count,
            "conflict_count": self.conflict_count,
            "summary": self.summary,
        }


@dataclass
class SynthesisResult:
    """Complete cross-source synthesis."""

    themes: list[ThemeSynthesis]
    areas_of_consensus: list[str] = field(default_factory=list)
    areas_of_conflict: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "themes": [t.to_dict() for t in self.themes],
            "areas_of_consensus": self.areas_of_consensus,
            "areas_of_conflict": self.areas_of_conflict,
            "evidence_gaps": self.evidence_gaps,
        }
