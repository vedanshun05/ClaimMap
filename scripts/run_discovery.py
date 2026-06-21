"""
Run Paper Discovery for multiple queries and merge results.

Usage:
    python scripts/run_discovery.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.paper_discovery.agent import PaperDiscoveryAgent
from src.paper_discovery.relevance import deduplicate_papers
from src.shared.config import config
from src.shared.utils import load_json, save_json


QUERIES = [
    "transformer attention",
    "self-attention mechanism neural network",
    "BERT language model 2018",
    "Ashish Vaswani Attention",
    "pre-training deep bidirectional transformers",
    "LLM",
    "what are the latest advances in neural network architectures for natural language processing",
    "transformer@attention#123",
    "1706.03762",
]


async def run_all_queries():
    """Run discovery for all queries and merge results."""
    agent = PaperDiscoveryAgent()
    all_papers = []

    print("=" * 60)
    print("PAPER DISCOVERY - Running 9 queries with arXiv + Semantic Scholar")
    print("=" * 60)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n[{i}/9] Query: '{query}'")
        print("-" * 40)

        try:
            papers = await agent.discover(query)
            all_papers.extend(papers)
            print(f"  → Found {len(papers)} papers")
        except Exception as e:
            print(f"  → Error: {e}")

    print("\n" + "=" * 60)
    print(f"Total papers before deduplication: {len(all_papers)}")

    # Deduplicate
    all_papers = deduplicate_papers(all_papers)
    print(f"Total papers after deduplication: {len(all_papers)}")

    # Save merged results
    filepath = config.data_dir / config.discovered_papers_file
    save_json(all_papers, filepath)
    print(f"\nSaved {len(all_papers)} papers to {filepath}")

    return all_papers


def main():
    papers = asyncio.run(run_all_queries())

    print("\n" + "=" * 60)
    print("TOP 10 PAPERS BY RELEVANCE:")
    print("=" * 60)
    for i, paper in enumerate(papers[:10], 1):
        print(f"\n{i}. {paper['title'][:70]}...")
        print(f"   ID: {paper['paper_id']}")
        print(f"   Source: {paper['source']} | Score: {paper.get('relevance_score', 0):.3f}")


if __name__ == "__main__":
    main()
