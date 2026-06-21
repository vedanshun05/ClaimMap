"""Relevance scoring for paper discovery."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoredPaper:
    """Paper with relevance score."""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    source: str
    relevance_score: float
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
            "relevance_score": round(self.relevance_score, 3),
            "citation_count": self.citation_count,
            "year": self.year,
        }


class RelevanceScorer:
    """Scores papers based on query relevance."""

    def __init__(self, query: str):
        self.query = query.lower()
        self.query_terms = set(self.query.split())

    def score(self, paper: dict[str, Any]) -> float:
        """
        Calculate relevance score for a paper.

        Score is based on:
        - Title keyword matches (highest weight)
        - Abstract keyword matches (medium weight)
        - Citation count (small boost)
        """
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()
        citation_count = paper.get("citation_count", 0) or 0

        title_matches = sum(1 for term in self.query_terms if term in title)
        abstract_matches = sum(1 for term in self.query_terms if term in abstract)

        title_score = title_matches * 0.5
        abstract_score = abstract_matches * 0.2

        citation_boost = min(citation_count / 1000, 0.1)

        total_score = title_score + abstract_score + citation_boost

        return min(total_score, 1.0)

    def score_and_rank(self, papers: list[dict[str, Any]]) -> list[ScoredPaper]:
        """Score all papers and return sorted by relevance."""
        scored = []
        for paper in papers:
            score = self.score(paper)
            scored.append(
                ScoredPaper(
                    paper_id=paper.get("paper_id", ""),
                    title=paper.get("title", ""),
                    authors=paper.get("authors", []),
                    abstract=paper.get("abstract", ""),
                    url=paper.get("url", ""),
                    source=paper.get("source", ""),
                    relevance_score=score,
                    citation_count=paper.get("citation_count", 0) or 0,
                    year=paper.get("year"),
                )
            )

        scored.sort(key=lambda p: p.relevance_score, reverse=True)
        return scored


def deduplicate_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate papers based on title similarity.

    Uses simple lowercase comparison - papers with identical
    lowercase titles are considered duplicates.
    """
    seen_titles: set[str] = set()
    unique_papers = []

    for paper in papers:
        title_lower = paper.get("title", "").lower().strip()
        if title_lower and title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_papers.append(paper)

    return unique_papers
