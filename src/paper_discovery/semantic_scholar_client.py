"""Semantic Scholar API client for paper discovery."""

import os
from typing import Any

import httpx


class SemanticScholarClient:
    """Client for Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: str | None = None, max_results: int = 20):
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.max_results = max_results
        self.timeout = 30.0

    def _get_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        return headers

    async def search(self, query: str, max_results: int | None = None) -> list[dict[str, Any]]:
        """
        Search Semantic Scholar for papers.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        max_results = max_results or self.max_results

        fields = [
            "paperId",
            "title",
            "authors",
            "abstract",
            "url",
            "year",
            "citationCount",
            "externalIds",
        ]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.BASE_URL}/paper/search",
                params={
                    "query": query,
                    "limit": max_results,
                    "fields": ",".join(fields),
                },
                headers=self._get_headers(),
            )

            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get("data", []):
                external_ids = item.get("externalIds", {}) or {}
                arxiv_id = external_ids.get("ArXiv", "")

                papers.append({
                    "paper_id": f"arxiv:{arxiv_id}" if arxiv_id else item.get("paperId", ""),
                    "title": item.get("title", ""),
                    "authors": [a.get("name", "") for a in item.get("authors", []) if a.get("name")],
                    "abstract": item.get("abstract", "") or "",
                    "url": item.get("url", ""),
                    "source": "semantic_scholar",
                    "year": item.get("year"),
                    "citation_count": item.get("citationCount", 0),
                })

            return papers

    async def get_paper(self, paper_id: str) -> dict[str, Any] | None:
        """Get a specific paper by ID."""
        fields = [
            "paperId",
            "title",
            "authors",
            "abstract",
            "url",
            "year",
            "citationCount",
            "externalIds",
            "openAccessPdf",
        ]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/paper/{paper_id}",
                    params={"fields": ",".join(fields)},
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()
            except Exception:
                return None

    async def get_paper_pdf_url(self, paper_id: str) -> str | None:
        """Get the PDF URL for a paper if available."""
        paper = await self.get_paper(paper_id)
        if paper and paper.get("openAccessPdf"):
            return paper["openAccessPdf"].get("url")
        return None


class SemanticScholarClientSync:
    """Synchronous wrapper for Semantic Scholar client."""

    def __init__(self, api_key: str | None = None, max_results: int = 20):
        self.async_client = SemanticScholarClient(api_key, max_results)

    def search(self, query: str, max_results: int | None = None) -> list[dict[str, Any]]:
        """Synchronous search."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.async_client.search(query, max_results))
