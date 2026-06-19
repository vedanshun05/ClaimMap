"""Backend models package."""

from .paper import Paper, Section, PaperSearchResult, SearchRequest, SearchResponse, IngestRequest
from .claim import Claim, ClaimExtractionResponse, ClaimTypeStats
from .relation import Relation, ConsensusScore, TopicGroup, SynthesisResult, SynthesisResponse
from .research_brief import ThemeSummary, ResearchBrief, BriefGenerationResponse, ExportRequest, ExportResponse

__all__ = [
    "Paper",
    "Section",
    "PaperSearchResult",
    "SearchRequest",
    "SearchResponse",
    "IngestRequest",
    "Claim",
    "ClaimExtractionResponse",
    "ClaimTypeStats",
    "Relation",
    "ConsensusScore",
    "TopicGroup",
    "SynthesisResult",
    "SynthesisResponse",
    "ThemeSummary",
    "ResearchBrief",
    "BriefGenerationResponse",
    "ExportRequest",
    "ExportResponse",
]
