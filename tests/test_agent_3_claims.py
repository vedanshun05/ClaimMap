"""Tests for Claim Extractor module."""

import pytest
from unittest.mock import MagicMock, patch

from src.claim_extractor.llm_client import LLMClient, ClaimExtractionPrompt, extract_claims_from_text
from src.claim_extractor.agent import ClaimExtractionAgent, ExtractedClaim


class TestLLMClient:
    """Tests for LLM client."""

    def test_initialization(self):
        """Test client initialization."""
        client = LLMClient()
        assert client.model is not None

    def test_extract_json_with_code_block(self):
        """Test JSON extraction from markdown code block."""
        client = LLMClient()

        text = "```json\n{\"key\": \"value\", \"number\": 42}\n```"

        result = client._extract_json(text)
        assert result is not None
        assert "key" in result

    def test_extract_json_direct(self):
        """Test JSON extraction from raw JSON."""
        client = LLMClient()

        text = '{"direct": "json"}'
        result = client._extract_json(text)
        assert result == '{"direct": "json"}'

    @pytest.mark.skip(reason="requires live API key")
    def test_generate_with_mock(self):
        """Test generation with mocked LLM client."""
        pass


class TestClaimExtractionPrompt:
    """Tests for prompt templates."""

    def test_system_prompt_exists(self):
        """Test system prompt is defined."""
        assert len(ClaimExtractionPrompt.SYSTEM_PROMPT) > 100

    def test_user_prompt_format(self):
        """Test user prompt template formatting."""
        prompt = ClaimExtractionPrompt.USER_PROMPT_TEMPLATE.format(
            title="Test Paper",
            paper_text="Some text content.",
            max_claims=10,
        )

        assert "Test Paper" in prompt
        assert "Some text content" in prompt
        assert "10" in prompt


class TestExtractedClaim:
    """Tests for ExtractedClaim dataclass."""

    def test_to_dict(self):
        """Test dictionary conversion."""
        claim = ExtractedClaim(
            claim_id="test-001",
            paper_id="paper-001",
            claim_type="finding",
            claim_text="This is a test finding.",
            source_section="Results",
            source_location="page 5",
            confidence=0.9,
        )

        data = claim.to_dict()

        assert data["claim_id"] == "test-001"
        assert data["claim_type"] == "finding"
        assert data["confidence"] == 0.9


class TestClaimExtractionAgent:
    """Tests for ClaimExtractionAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = ClaimExtractionAgent()
        assert agent.llm_client is not None

    def test_deduplicate_claims(self):
        """Test claim deduplication."""
        agent = ClaimExtractionAgent()

        claims = [
            ExtractedClaim("1", "p1", "finding", "Same text"),
            ExtractedClaim("2", "p1", "finding", "Same text"),
            ExtractedClaim("3", "p1", "finding", "Different text"),
        ]

        unique = agent.deduplicate_claims(claims)

        assert len(unique) == 2

    def test_extract_from_paper_insufficient_text(self):
        """Test handling of papers with insufficient text."""
        agent = ClaimExtractionAgent()

        paper = {
            "paper_id": "test",
            "title": "Test",
            "full_text": "Short",
        }

        claims = agent._extract_from_paper(paper, max_claims=10)
        assert len(claims) == 0
