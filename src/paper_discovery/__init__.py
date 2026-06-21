"""Paper Discovery module - Search and rank papers from arXiv and Semantic Scholar."""

from .arxiv_client import ArxivClient, ArxivPaper
from .semantic_scholar_client import SemanticScholarClient, SemanticScholarClientSync
from .relevance import RelevanceScorer, ScoredPaper, deduplicate_papers
from .agent import PaperDiscoveryAgent

__all__ = [
    "ArxivClient",
    "ArxivPaper",
    "SemanticScholarClient",
    "SemanticScholarClientSync",
    "RelevanceScorer",
    "ScoredPaper",
    "deduplicate_papers",
    "PaperDiscoveryAgent",
]
