"""Tests for Paper Discovery module."""

import pytest
from unittest.mock import MagicMock, patch

from src.paper_discovery.arxiv_client import ArxivClient, ArxivPaper
from src.paper_discovery.relevance import RelevanceScorer, deduplicate_papers, ScoredPaper
from src.paper_discovery.agent import PaperDiscoveryAgent


class TestArxivClient:
    """Tests for arXiv client."""

    def test_search_returns_list(self):
        """Test that search returns a list of papers."""
        client = ArxivClient(max_results=5)
        with patch("arxiv.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.results.return_value = iter([])

            papers = client.search("machine learning")
            assert isinstance(papers, list)

    def test_search_with_mock_results(self):
        """Test search with mocked results."""
        client = ArxivClient(max_results=3)

        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/2301.12345"
        mock_result.title = "Test Paper"
        mock_result.authors = [MagicMock(name="John Doe")]
        mock_result.summary = "This is a test abstract."
        mock_result.pdf_url = "http://arxiv.org/pdf/2301.12345"
        mock_result.published = MagicMock()
        mock_result.published.date.return_value.__str__ = MagicMock(return_value="2023-01-01")

        with patch("arxiv.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.results.return_value = iter([mock_result])

            papers = client.search("test query")

            assert len(papers) == 1
            assert papers[0].title == "Test Paper"
            assert papers[0].paper_id == "arXiv:2301.12345"


class TestRelevanceScorer:
    """Tests for relevance scoring."""

    def test_score_higher_for_title_match(self):
        """Test that title matches score higher than abstract matches."""
        scorer = RelevanceScorer("machine learning")

        paper_with_title_match = {
            "title": "Machine Learning for Everyone",
            "abstract": "A book about algorithms.",
            "citation_count": 10,
        }

        paper_with_abstract_only = {
            "title": "Great Algorithms",
            "abstract": "Machine learning techniques explained.",
            "citation_count": 10,
        }

        title_score = scorer.score(paper_with_title_match)
        abstract_score = scorer.score(paper_with_abstract_only)

        assert title_score > abstract_score

    def test_citation_boost(self):
        """Test that higher citation counts get a small boost."""
        scorer = RelevanceScorer("test")

        low_cite_paper = {
            "title": "Test Title",
            "abstract": "test abstract content",
            "citation_count": 10,
        }

        high_cite_paper = {
            "title": "Test Title",
            "abstract": "test abstract content",
            "citation_count": 1000,
        }

        low_score = scorer.score(low_cite_paper)
        high_score = scorer.score(high_cite_paper)

        assert high_score > low_score

    def test_score_and_rank(self):
        """Test scoring and ranking multiple papers."""
        scorer = RelevanceScorer("neural network")

        papers = [
            {"title": "Neural Networks", "abstract": "Deep learning.", "citation_count": 100},
            {"title": "Dogs", "abstract": "Man's best friend.", "citation_count": 50},
            {"title": "Neural Network Regularization", "abstract": "Improving networks.", "citation_count": 75},
        ]

        ranked = scorer.score_and_rank(papers)

        assert len(ranked) == 3
        assert ranked[0].title == "Neural Networks"
        assert ranked[0].relevance_score >= ranked[1].relevance_score
        assert ranked[1].relevance_score >= ranked[2].relevance_score


class TestDeduplication:
    """Tests for paper deduplication."""

    def test_exact_duplicate_removed(self):
        """Test that exact duplicate titles are removed."""
        papers = [
            {"paper_id": "1", "title": "Test Paper"},
            {"paper_id": "2", "title": "Test Paper"},
            {"paper_id": "3", "title": "Different Paper"},
        ]

        unique = deduplicate_papers(papers)

        assert len(unique) == 2

    def test_case_insensitive_dedup(self):
        """Test that deduplication is case insensitive."""
        papers = [
            {"paper_id": "1", "title": "Test Paper"},
            {"paper_id": "2", "title": "test paper"},
            {"paper_id": "3", "title": "TEST PAPER"},
        ]

        unique = deduplicate_papers(papers)

        assert len(unique) == 1


class TestPaperDiscoveryAgent:
    """Integration tests for PaperDiscoveryAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = PaperDiscoveryAgent(max_papers_per_source=10)

        assert agent.arxiv_client is not None
        assert agent.ss_client is not None
        assert agent.max_papers_per_source == 10
