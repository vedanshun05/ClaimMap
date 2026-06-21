"""PDF extraction client for document ingestion."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExtractedPDF:
    """Extracted content from a PDF."""

    paper_id: str
    full_text: str
    pages: int
    sections: dict[str, str]


class PDFExtractor:
    """Extract text content from PDFs."""

    def __init__(self):
        self.section_patterns = {
            "abstract": r"(?:^|\n)(?:abstract|summary|synopsis)(?:\s*:|\s*\n)",
            "introduction": r"(?:^|\n)(?:introduction|background|1\.\s*Introduction)(?:\s*:|\s*\n)",
            "method": r"(?:^|\n)(?:method|methodology|approach|experimental|2\.\s*Method)(?:\s*:|\s*\n)",
            "results": r"(?:^|\n)(?:result|findings|experiment|3\.\s*Result)(?:\s*:|\s*\n)",
            "discussion": r"(?:^|\n)(?:discussion|analysis|4\.\s*Discussion)(?:\s*:|\s*\n)",
            "conclusion": r"(?:^|\n)(?:conclusion|conclusions|summary and outlook|5\.\s*Conclusion)(?:\s*:|\s*\n)",
            "limitations": r"(?:^|\n)(?:limitation|future work|不足|展望)(?:\s*:|\s*\n)",
            "references": r"(?:^|\n)(?:reference|bibliography|work cited)(?:\s*:|\s*\n)",
        }

    def extract(self, pdf_path: Path, paper_id: str) -> ExtractedPDF | None:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file
            paper_id: Identifier for the paper

        Returns:
            ExtractedPDF object, or None if extraction fails
        """
        try:
            import fitz

            doc = fitz.open(str(pdf_path))
            pages = len(doc)

            full_text = ""
            for page in doc:
                text = page.get_text()
                full_text += text + "\n"

            doc.close()

            sections = self._extract_sections(full_text)

            return ExtractedPDF(
                paper_id=paper_id,
                full_text=full_text.strip(),
                pages=pages,
                sections=sections,
            )
        except Exception as e:
            print(f"[PDF Extractor] Error extracting {pdf_path}: {e}")
            return None

    def _extract_sections(self, text: str) -> dict[str, str]:
        """Attempt to extract named sections from text."""
        sections = {}

        text_lower = text.lower()

        for section_name, pattern in self.section_patterns.items():
            matches = list(re.finditer(pattern, text_lower, re.MULTILINE))

            if matches:
                start = matches[0].start()

                if len(matches) > 1:
                    end = matches[1].start()
                else:
                    end = len(text_lower)

                section_text = text[start:end].strip()

                section_text = re.sub(r"\n{3,}", "\n\n", section_text)

                sections[section_name] = section_text

        return sections

    def extract_from_arxiv_id(self, arxiv_id: str, download_dir: Path) -> ExtractedPDF | None:
        """
        Download and extract an arXiv PDF.

        Args:
            arxiv_id: arXiv paper ID (e.g., "2301.12345")
            download_dir: Directory to download PDF to

        Returns:
            ExtractedPDF object, or None if download/extraction fails
        """
        try:
            from ..paper_discovery.arxiv_client import ArxivClient

            client = ArxivClient()
            pdf_path = client.download_pdf(arxiv_id, str(download_dir))

            if pdf_path and Path(pdf_path).exists():
                return self.extract(Path(pdf_path), f"arXiv:{arxiv_id}")

            return None
        except Exception as e:
            print(f"[PDF Extractor] Error downloading arXiv paper {arxiv_id}: {e}")
            return None
