"""
Agent 1: Paper Discovery

Given a research question, search academic sources (arXiv, Semantic Scholar)
and return a ranked list of relevant papers.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.config import config, api_config
from src.shared.utils import save_json
from .arxiv_client import ArxivClient
from .semantic_scholar_client import SemanticScholarClientSync
from .relevance import RelevanceScorer, deduplicate_papers


class PaperDiscoveryAgent:
    """
    Agent responsible for paper discovery from academic sources.

    Searches arXiv and Semantic Scholar, ranks results by relevance,
    and saves discovered papers to the shared data store.
    """

    def __init__(self, max_papers_per_source: int = 20):
        self.arxiv_client = ArxivClient(max_results=max_papers_per_source)
        self.ss_client = SemanticScholarClientSync(
            api_key=api_config.semantic_scholar_api_key,
            max_results=max_papers_per_source,
        )
        self.max_papers_per_source = max_papers_per_source

    async def discover(
        self,
        query: str,
        max_total: int | None = None,
    ) -> list[dict]:
        """
        Discover papers from all sources for a given query.

        Args:
            query: Research question or topic
            max_total: Maximum total papers to return (default: config.max_papers_per_query)

        Returns:
            List of ranked paper dictionaries
        """
        max_total = max_total or config.max_papers_per_query

        print(f"[Agent 1] Discovering papers for query: '{query}'")

        papers = []

        print("[Agent 1] Searching arXiv...")
        try:
            arxiv_papers = self.arxiv_client.search(query, self.max_papers_per_source)
            for p in arxiv_papers:
                papers.append({
                    "paper_id": p.paper_id,
                    "title": p.title,
                    "authors": p.authors,
                    "abstract": p.abstract,
                    "url": p.url,
                    "source": "arxiv",
                    "citation_count": 0,
                })
            print(f"[Agent 1] Found {len(arxiv_papers)} papers on arXiv")
        except Exception as e:
            print(f"[Agent 1] arXiv search error: {e}")

        print("[Agent 1] Searching Semantic Scholar...")
        try:
            ss_papers = await asyncio.to_thread(
                self.ss_client.search, query, self.max_papers_per_source
            )
            papers.extend(ss_papers)
            print(f"[Agent 1] Found {len(ss_papers)} papers on Semantic Scholar")
        except Exception as e:
            print(f"[Agent 1] Semantic Scholar search error: {e}")

        print(f"[Agent 1] Total papers before deduplication: {len(papers)}")

        papers = deduplicate_papers(papers)
        print(f"[Agent 1] Papers after deduplication: {len(papers)}")

        scorer = RelevanceScorer(query)
        ranked = scorer.score_and_rank(papers)

        result = [p.to_dict() for p in ranked[:max_total]]
        print(f"[Agent 1] Returning top {len(result)} papers by relevance")

        return result

    def save_discovered_papers(self, papers: list[dict]) -> Path:
        """Save discovered papers to the data directory."""
        filepath = config.data_dir / config.discovered_papers_file
        save_json(papers, filepath)
        print(f"[Agent 1] Saved {len(papers)} papers to {filepath}")
        return filepath


def main():
    """CLI entry point for Agent 1."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.agent_1_discovery <research_query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    agent = PaperDiscoveryAgent()
    papers = asyncio.run(agent.discover(query))
    agent.save_discovered_papers(papers)

    print("\n[Agent 1] Top 5 discovered papers:")
    for i, paper in enumerate(papers[:5], 1):
        print(f"  {i}. {paper['title'][:60]}...")
        print(f"     Score: {paper['relevance_score']:.3f} | Source: {paper['source']}")


if __name__ == "__main__":
    main()
