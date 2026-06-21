"""
Document Processor

Ingest full-text PDFs, extract abstract, methodology, key findings,
limitations, and conclusion as structured fields.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.config import config
from src.shared.utils import load_json, save_json, papers_from_dict
from .pdf_extractor import PDFExtractor
from .field_extractor import FieldExtractor, StructuredPaper


class DocumentIngestionAgent:
    """
    Agent responsible for document ingestion and structured extraction.

    Takes discovered papers (with PDFs) and extracts structured fields.
    """

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.field_extractor = FieldExtractor()

    def ingest_papers(self, papers: list[dict] | None = None) -> list[StructuredPaper]:
        """
        Ingest papers and extract structured fields.

        Args:
            papers: List of paper dicts (from Agent 1). If None, loads from data store.

        Returns:
            List of StructuredPaper objects
        """
        if papers is None:
            filepath = config.data_dir / config.discovered_papers_file
            data = load_json(filepath)
            papers = papers_from_dict(data)

        print(f"[Agent 2] Ingesting {len(papers)} papers...")

        ingested = []
        for paper in papers:
            result = self._ingest_single_paper(paper)
            if result:
                ingested.append(result)

        print(f"[Agent 2] Successfully ingested {len(ingested)} papers")
        return ingested

    def _ingest_single_paper(self, paper) -> StructuredPaper | None:
        """Ingest a single paper."""
        # Handle both dict and PaperMetadata objects
        if hasattr(paper, 'to_dict'):
            paper = paper.to_dict()

        paper_id = paper.get("paper_id", "")
        title = paper.get("title", "")
        source = paper.get("source", "")
        url = paper.get("url", "")

        print(f"[Agent 2] Processing: {title[:50]}...")

        # Check for local PDF first
        pdf_path = self._find_local_pdf(paper_id)

        # If not found and it's arXiv, try to download
        if not pdf_path and source == "arxiv":
            print(f"[Agent 2] Local PDF not found, attempting download for {paper_id}...")
            pdf_path = self._download_arxiv_pdf(paper_id)

        if not pdf_path or not pdf_path.exists():
            print(f"[Agent 2] Could not find PDF for {paper_id}")
            pdf = None
        else:
            pdf = self.pdf_extractor.extract(pdf_path, paper_id)

        if pdf:
            structured = self.field_extractor.extract(pdf, title)
            structured.source = source
            return structured

        return None

    def _download_arxiv_pdf(self, paper_id: str) -> Path | None:
        """Download arXiv PDF."""
        download_dir = config.data_dir / "pdfs"
        download_dir.mkdir(parents=True, exist_ok=True)

        try:
            pdf_path = self.pdf_extractor.extract_from_arxiv_id(paper_id, download_dir)
            if pdf_path:
                return Path(pdf_path)
        except Exception as e:
            print(f"[Agent 2] Error downloading {paper_id}: {e}")

        return None

    def _find_local_pdf(self, paper_id: str) -> Path | None:
        """Find local PDF for a paper."""
        pdf_dir = config.data_dir / "pdfs"

        for ext in [".pdf", ".PDF"]:
            pdf_path = pdf_dir / f"{paper_id}{ext}"
            if pdf_path.exists():
                return pdf_path

        return None

    def _create_from_abstract_only(self, paper: dict) -> None:
        """Create minimal structured paper from abstract only."""
        return None

    def save_ingested_papers(self, papers: list[StructuredPaper]) -> Path:
        """Save ingested papers to the data directory."""
        filepath = config.data_dir / config.ingested_papers_file
        data = [p.to_dict() for p in papers]
        save_json(data, filepath)
        print(f"[Agent 2] Saved {len(papers)} papers to {filepath}")
        return filepath


def main():
    """CLI entry point for Agent 2."""
    agent = DocumentIngestionAgent()
    papers = agent.ingest_papers()
    agent.save_ingested_papers(papers)

    print("\n[Agent 2] Sample extracted paper:")
    if papers:
        p = papers[0]
        print(f"  Title: {p.title[:50]}...")
        print(f"  Abstract length: {len(p.abstract)} chars")
        print(f"  Methodology length: {len(p.methodology)} chars")
        print(f"  Findings count: {len(p.key_findings)}")
        print(f"  Limitations count: {len(p.limitations)}")


if __name__ == "__main__":
    main()
