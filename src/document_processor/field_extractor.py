"""Structured field extraction from PDFs."""

import re
from dataclasses import dataclass
from typing import Any

from .pdf_extractor import ExtractedPDF


@dataclass
class StructuredPaper:
    """Paper with extracted structured fields."""

    paper_id: str
    title: str = ""
    abstract: str = ""
    methodology: str = ""
    key_findings: list[str] = None
    limitations: list[str] = None
    conclusion: str = ""
    full_text: str = ""
    pages: int = 0

    def __post_init__(self):
        if self.key_findings is None:
            self.key_findings = []
        if self.limitations is None:
            self.limitations = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "methodology": self.methodology,
            "key_findings": self.key_findings,
            "limitations": self.limitations,
            "conclusion": self.conclusion,
            "full_text": self.full_text,
            "pages": self.pages,
        }


class FieldExtractor:
    """Extract structured fields from extracted PDF content."""

    def __init__(self):
        self.bullet_patterns = [
            r"^\s*[-•∗◦▪]\s+",
            r"^\s*\d+[.)]\s+",
            r"^\s*\([a-z]\)\s+",
        ]

    def extract(self, pdf: ExtractedPDF, title: str = "") -> StructuredPaper:
        """
        Extract structured fields from an extracted PDF.

        Args:
            pdf: ExtractedPDF object with full text and sections
            title: Paper title (if known)

        Returns:
            StructuredPaper object
        """
        sections = pdf.sections
        full_text = pdf.full_text

        abstract = self._extract_abstract(sections, full_text)
        methodology = self._extract_methodology(sections, full_text)
        key_findings = self._extract_findings(sections, full_text)
        limitations = self._extract_limitations(sections, full_text)
        conclusion = self._extract_conclusion(sections, full_text)

        return StructuredPaper(
            paper_id=pdf.paper_id,
            title=title,
            abstract=abstract,
            methodology=methodology,
            key_findings=key_findings,
            limitations=limitations,
            conclusion=conclusion,
            full_text=full_text,
            pages=pdf.pages,
        )

    def _extract_abstract(self, sections: dict, full_text: str) -> str:
        """Extract abstract from sections or beginning of text."""
        if "abstract" in sections:
            abstract_text = sections["abstract"]
            abstract_text = self._clean_text(abstract_text)
            if len(abstract_text) > 50:
                return abstract_text[:2000]

        first_paras = self._get_first_paragraphs(full_text, n=2)
        if first_paras:
            return first_paras[:2000]

        return ""

    def _extract_methodology(self, sections: dict, full_text: str) -> str:
        """Extract methodology section."""
        for key in ["method", "methodology", "approach", "experimental"]:
            if key in sections:
                method_text = sections[key]
                method_text = self._clean_text(method_text)
                return method_text[:3000]

        return ""

    def _extract_findings(self, sections: dict, full_text: str) -> list[str]:
        """Extract key findings as bullet points."""
        findings = []

        if "results" in sections:
            results_text = sections["results"]
            bullets = self._extract_bullet_points(results_text)
            findings.extend(bullets)

        if "discussion" in sections:
            discussion_text = sections["discussion"]
            bullets = self._extract_bullet_points(discussion_text)
            findings.extend(bullets)

        unique_findings = []
        seen = set()
        for f in findings:
            f_lower = f.lower()
            if f_lower not in seen and len(f) > 30:
                seen.add(f_lower)
                unique_findings.append(f)

        return unique_findings[:10]

    def _extract_limitations(self, sections: dict, full_text: str) -> list[str]:
        """Extract limitations as bullet points."""
        limitations = []

        for key in ["limitations", "future work"]:
            if key in sections:
                text = sections[key]
                bullets = self._extract_bullet_points(text)
                limitations.extend(bullets)

        unique_limitations = []
        seen = set()
        for l in limitations:
            l_lower = l.lower()
            if l_lower not in seen and len(l) > 20:
                seen.add(l_lower)
                unique_limitations.append(l)

        return unique_limitations[:5]

    def _extract_conclusion(self, sections: dict, full_text: str) -> str:
        """Extract conclusion section."""
        if "conclusion" in sections:
            conclusion_text = sections["conclusion"]
            conclusion_text = self._clean_text(conclusion_text)
            return conclusion_text[:2000]

        last_paras = self._get_last_paragraphs(full_text, n=2)
        if last_paras:
            return last_paras[:2000]

        return ""

    def _extract_bullet_points(self, text: str) -> list[str]:
        """Extract bullet points from text."""
        lines = text.split("\n")
        bullets = []

        for line in lines:
            line = line.strip()
            for pattern in self.bullet_patterns:
                if re.match(pattern, line):
                    bullet_text = re.sub(pattern, "", line).strip()
                    if len(bullet_text) > 20:
                        bullets.append(bullet_text)
                    break

        return bullets

    def _get_first_paragraphs(self, text: str, n: int = 1) -> str:
        """Get the first N paragraphs from text."""
        paragraphs = text.split("\n\n")
        result = []

        for para in paragraphs:
            para = para.strip()
            if len(para) > 100:
                result.append(para)
            if len(result) >= n:
                break

        return "\n\n".join(result)

    def _get_last_paragraphs(self, text: str, n: int = 1) -> str:
        """Get the last N paragraphs from text."""
        paragraphs = text.split("\n\n")
        result = []

        for para in reversed(paragraphs):
            para = para.strip()
            if len(para) > 100:
                result.insert(0, para)
            if len(result) >= n:
                break

        return "\n\n".join(result)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
