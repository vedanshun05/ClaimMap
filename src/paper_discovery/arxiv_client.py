"""arXiv API client for paper discovery."""

import arxiv
from dataclasses import dataclass
from typing import Iterator


@dataclass
class ArxivPaper:
    """Simplified arXiv paper representation."""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    published_date: str = ""


class ArxivClient:
    """Client for searching arXiv papers."""

    def __init__(self, max_results: int = 20):
        self.max_results = max_results

    def search(self, query: str, max_results: int | None = None) -> list[ArxivPaper]:
        """
        Search arXiv for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results (default: self.max_results)

        Returns:
            List of ArxivPaper objects
        """
        max_results = max_results or self.max_results

        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []
        for result in client.results(search):
            papers.append(
                ArxivPaper(
                    paper_id=f"arXiv:{result.entry_id.split('/')[-1]}",
                    title=result.title,
                    authors=[a.name for a in result.authors],
                    abstract=result.summary.replace("\n", " "),
                    url=result.pdf_url or result.entry_id,
                    published_date=str(result.published.date()) if result.published else "",
                )
            )

        return papers

    def get_paper(self, paper_id: str) -> ArxivPaper | None:
        """Get a specific paper by arXiv ID."""
        client = arxiv.Client()

        try:
            search = arxiv.Search(id_list=[paper_id.replace("arXiv:", "")])
            result = next(client.results(search))

            return ArxivPaper(
                paper_id=f"arXiv:{result.entry_id.split('/')[-1]}",
                title=result.title,
                authors=[a.name for a in result.authors],
                abstract=result.summary.replace("\n", " "),
                url=result.pdf_url or result.entry_id,
                published_date=str(result.published.date()) if result.published else "",
            )
        except Exception:
            return None

    def download_pdf(self, paper_id: str, output_dir: str) -> str | None:
        """
        Download PDF for a paper.

        Args:
            paper_id: arXiv paper ID
            output_dir: Directory to save PDF

        Returns:
            Path to downloaded PDF, or None if failed
        """
        import os

        client = arxiv.Client()
        os.makedirs(output_dir, exist_ok=True)

        try:
            paper = self.get_paper(paper_id)
            if not paper:
                return None

            download = arxiv.Downloader(
                client=client,
                dirpath=output_dir,
                filename_template="arXiv_{paper_id}.pdf",
            )

            result = download.download_single(paper.entry_id)
            return result
        except Exception:
            return None
