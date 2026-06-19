"""Tests for Document Processor module."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.document_processor.pdf_extractor import PDFExtractor, ExtractedPDF
from src.document_processor.field_extractor import FieldExtractor, StructuredPaper
from src.document_processor.agent import DocumentIngestionAgent


class TestPDFExtractor:
    """Tests for PDF extraction."""

    def test_extract_sections(self):
        """Test section extraction patterns."""
        extractor = PDFExtractor()

        text = """
ABSTRACT
This is the abstract content describing the paper.

INTRODUCTION
This is the introduction with background information.

METHOD
This section describes the methodology used.

RESULTS
These are the results showing our findings.
"""

        sections = extractor._extract_sections(text)

        assert "abstract" in sections or len(sections) > 0

    def test_extract_with_mock_pdf(self):
        """Test extraction with mocked PDF."""
        extractor = PDFExtractor()

        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF text content.\n\nWith multiple paragraphs."
        mock_doc.__iter__ = lambda self: iter([mock_page])
        mock_doc.__len__ = lambda self: 1
        mock_doc.close = MagicMock()

        with patch("fitz.open", return_value=mock_doc):
            result = extractor.extract(Path("test.pdf"), "test-paper")

            assert result is not None
            assert result.paper_id == "test-paper"
            assert len(result.full_text) > 0


class TestFieldExtractor:
    """Tests for structured field extraction."""

    def test_extract_abstract(self):
        """Test abstract extraction."""
        extractor = FieldExtractor()

        sections = {
            "abstract": "This paper presents a new method for machine learning."
        }

        result = extractor._extract_abstract(sections, "")

        assert len(result) > 0

    def test_extract_methodology(self):
        """Test methodology extraction."""
        extractor = FieldExtractor()

        sections = {
            "methodology": "Methodology\nWe used deep learning with transformers."
        }

        result = extractor._extract_methodology(sections, "")
        assert "deep learning" in result.lower() or "transformers" in result.lower()

    def test_extract_bullet_points(self):
        """Test bullet point extraction."""
        extractor = FieldExtractor()

        text = """
Results:
- First finding about accuracy
- Second finding about speed
• Third finding about efficiency
1. Fourth finding about cost
        """

        bullets = extractor._extract_bullet_points(text)

        assert len(bullets) >= 2

    def test_clean_text(self):
        """Test text cleaning."""
        extractor = FieldExtractor()

        dirty = "  This   is    dirty  \n\n\n\ntext  "
        clean = extractor._clean_text(dirty)

        assert "  " not in clean
        assert "\n\n\n\n" not in clean


class TestStructuredPaper:
    """Tests for StructuredPaper dataclass."""

    def test_to_dict(self):
        """Test dictionary conversion."""
        paper = StructuredPaper(
            paper_id="test-001",
            title="Test Paper",
            abstract="This is an abstract.",
            key_findings=["Finding 1", "Finding 2"],
        )

        data = paper.to_dict()

        assert data["paper_id"] == "test-001"
        assert data["title"] == "Test Paper"
        assert len(data["key_findings"]) == 2


class TestDocumentIngestionAgent:
    """Integration tests for DocumentIngestionAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = DocumentIngestionAgent()

        assert agent.pdf_extractor is not None
        assert agent.field_extractor is not None
