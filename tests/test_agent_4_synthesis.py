"""Tests for Synthesis Engine module."""

import pytest
from unittest.mock import MagicMock

from src.synthesis_engine.clustering import ThematicClusterer, ClaimCluster
from src.synthesis_engine.consensus import ConsensusDetector, ConflictDetector
from src.synthesis_engine.agent import CrossSourceSynthesisAgent, SynthesisTheme
from src.shared.models import Claim


class TestThematicClusterer:
    """Tests for thematic clustering."""

    def test_identify_theme_by_keyword(self):
        """Test theme identification by keywords."""
        clusterer = ThematicClusterer()

        assert clusterer._identify_theme("The model achieves 95% accuracy") == "accuracy"
        assert clusterer._identify_theme("Fast inference with low latency") == "efficiency"
        assert clusterer._identify_theme("Transformer architecture") == "architecture"

    def test_identify_theme_returns_none_for_unknown(self):
        """Test unknown theme returns None."""
        clusterer = ThematicClusterer()

        result = clusterer._identify_theme("xyz123 unknown topic")
        assert result is None

    def test_cluster_claims(self):
        """Test claim clustering."""
        clusterer = ThematicClusterer()

        claims = [
            Claim("c1", "p1", "finding", "Achieves 95% accuracy"),
            Claim("c2", "p1", "finding", "Fast inference speed"),
            Claim("c3", "p2", "finding", "Model accuracy improved"),
            Claim("c4", "p3", "finding", "Completely unrelated claim xyz"),
        ]

        clusters = clusterer.cluster_claims(claims)

        assert len(clusters) >= 2
        accuracy_cluster = next((c for c in clusters if c.theme_id == "accuracy"), None)
        assert accuracy_cluster is not None
        assert len(accuracy_cluster.claim_ids) == 2

    def test_get_theme_name(self):
        """Test theme name conversion."""
        clusterer = ThematicClusterer()

        assert "Accuracy" in clusterer._get_theme_name("accuracy")
        assert "Efficiency" in clusterer._get_theme_name("efficiency")


class TestConsensusDetector:
    """Tests for consensus detection."""

    def test_detects_agreement(self):
        """Test agreement detection."""
        detector = ConsensusDetector()

        assert detector._indicates_agreement("The results confirm our hypothesis")
        assert detector._indicates_agreement("We demonstrate improved performance")
        assert detector._indicates_agreement("The model achieves state-of-the-art results")

    def test_detects_disagreement(self):
        """Test disagreement detection."""
        detector = ConsensusDetector()

        assert detector._indicates_disagreement("However, these results contradict")
        assert detector._indicates_disagreement("We question the validity of")
        assert detector._indicates_disagreement("These findings conflict with prior work")

    def test_analyze_consensus(self):
        """Test full consensus analysis."""
        detector = ConsensusDetector()

        claims = [
            Claim("c1", "p1", "finding", "The model demonstrates improved accuracy."),
            Claim("c2", "p2", "finding", "Results confirm the effectiveness."),
        ]

        result = detector.analyze_consensus(claims, {})

        assert result.consensus in ["strong", "moderate", "weak"]
        assert result.agreement_count >= 0


class TestConflictDetector:
    """Tests for conflict detection."""

    def test_find_conflicts(self):
        """Test conflict finding."""
        detector = ConflictDetector()

        claims = [
            Claim("c1", "p1", "finding", "The model improves accuracy by 10%"),
            Claim("c2", "p2", "finding", "The model degrades performance by 5%"),
        ]

        conflicts = detector.find_conflicts(claims)
        assert len(conflicts) >= 1

    def test_no_conflict_within_same_paper(self):
        """Test that same-paper claims are not flagged as conflicts."""
        detector = ConflictDetector()

        claims = [
            Claim("c1", "p1", "finding", "First finding"),
            Claim("c2", "p1", "finding", "Second finding"),
        ]

        conflicts = detector.find_conflicts(claims)
        assert len(conflicts) == 0


class TestSynthesisTheme:
    """Tests for SynthesisTheme."""

    def test_to_theme_synthesis(self):
        """Test conversion to ThemeSynthesis."""
        theme = SynthesisTheme(
            theme_id="accuracy",
            theme_name="Model Accuracy",
            claim_ids=["c1", "c2"],
            consensus="strong",
            agreement_count=2,
            conflict_count=0,
            summary="Strong consensus found.",
        )

        ts = theme.to_theme_synthesis()

        assert ts.theme_id == "accuracy"
        assert ts.consensus == "strong"
        assert len(ts.claim_ids) == 2


class TestCrossSourceSynthesisAgent:
    """Tests for CrossSourceSynthesisAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = CrossSourceSynthesisAgent()

        assert agent.clusterer is not None
        assert agent.consensus_detector is not None
        assert agent.conflict_detector is not None
