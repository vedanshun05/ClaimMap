"""Tests for Brief Generator module."""

import pytest
from pathlib import Path
from datetime import datetime

from src.brief_generator.template import BriefTemplate, CitationFormatter, BriefSection
from src.brief_generator.exporter import MarkdownExporter
from src.brief_generator.agent import BriefGenerationAgent


class TestBriefTemplate:
    """Tests for brief template."""

    def test_get_markdown_template(self):
        """Test template retrieval."""
        template = BriefTemplate.get_markdown_template()
        assert "Research Brief:" in template

    def test_format_theme_section(self):
        """Test theme section formatting."""
        template = BriefTemplate()

        theme = {
            "theme_name": "Model Accuracy",
            "claim_ids": ["c1", "c2"],
            "consensus": "strong",
            "summary": "Strong evidence supports accuracy improvements.",
        }

        result = template.format_theme_section(theme)

        assert "Model Accuracy" in result
        assert "Strong evidence" in result

    def test_format_claim_with_citation(self):
        """Test claim citation formatting."""
        template = BriefTemplate()

        claim = {
            "claim_text": "The model achieves 95% accuracy.",
            "claim_type": "finding",
            "source_section": "Results",
            "source_location": "page 5",
        }

        paper = {
            "title": "A Machine Learning Paper",
            "paper_id": "arXiv:2301.12345",
        }

        result = template.format_claim_with_citation(claim, paper)

        assert "95% accuracy" in result
        assert "Machine Learning Paper" in result


class TestCitationFormatter:
    """Tests for citation formatting."""

    def test_format_bibtex(self):
        """Test BibTeX formatting."""
        paper = {
            "paper_id": "arXiv:2301.12345",
            "title": "Test Paper Title",
            "authors": ["John Doe", "Jane Smith"],
            "year": "2023",
            "url": "https://arxiv.org/abs/2301.12345",
        }

        result = CitationFormatter.format_bibtex(paper)

        assert "@article{" in result
        assert "Test Paper Title" in result

    def test_format_apa_single_author(self):
        """Test APA formatting with single author."""
        paper = {
            "title": "Test Paper",
            "authors": ["John Doe"],
            "year": 2023,
        }

        result = CitationFormatter.format_apa(paper)

        assert "Doe (2023)" in result
        assert "Test Paper" in result

    def test_format_apa_multiple_authors(self):
        """Test APA formatting with multiple authors."""
        paper = {
            "title": "Test Paper",
            "authors": ["John Doe", "Jane Smith", "Bob Wilson"],
            "year": 2023,
        }

        result = CitationFormatter.format_apa(paper)

        assert "et al." in result
        assert "2023" in result

    def test_format_inline_citation(self):
        """Test inline citation formatting."""
        paper = {
            "authors": ["John Doe", "Jane Smith"],
            "year": 2023,
        }

        result = CitationFormatter.format_inline_citation(paper)

        assert "(Doe et al., 2023)" == result


class TestMarkdownExporter:
    """Tests for Markdown exporter."""

    def test_format_findings(self):
        """Test findings formatting."""
        template = BriefTemplate()
        exporter = MarkdownExporter(template)

        themes = [
            {
                "theme_name": "Accuracy",
                "claim_ids": ["c1"],
                "consensus": "strong",
                "summary": "Good consensus.",
            }
        ]

        result = exporter._format_findings(themes)

        assert "Accuracy" in result
        assert len(result) > 0

    def test_format_list(self):
        """Test list formatting."""
        template = BriefTemplate()
        exporter = MarkdownExporter(template)

        items = ["Item 1", "Item 2", "Item 3"]
        result = exporter._format_list(items)

        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_format_empty_list(self):
        """Test empty list formatting."""
        template = BriefTemplate()
        exporter = MarkdownExporter(template)

        result = exporter._format_list([])
        assert "None identified" in result

    def test_format_papers(self):
        """Test papers formatting."""
        template = BriefTemplate()
        exporter = MarkdownExporter(template)

        papers = [
            {"title": "Paper One", "url": "http://example.com/1"},
            {"title": "Paper Two", "url": "http://example.com/2"},
        ]

        result = exporter._format_papers(papers)

        assert "Paper One" in result
        assert "http://example.com/1" in result


class TestBriefGenerationAgent:
    """Tests for BriefGenerationAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = BriefGenerationAgent()

        assert agent.template is not None
        assert agent.markdown_exporter is not None
        assert agent.pdf_exporter is not None

    def test_get_recommended_papers(self):
        """Test paper recommendations."""
        agent = BriefGenerationAgent()

        papers = [
            {"paper_id": "p1", "title": "High Impact", "citation_count": 100},
            {"paper_id": "p2", "title": "Low Impact", "citation_count": 10},
        ]

        class MockSynthesis:
            themes = []

        recommendations = agent._get_recommended_papers(papers, MockSynthesis())

        assert len(recommendations) <= 5
