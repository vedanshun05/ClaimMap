"""Thematic clustering for claim synthesis."""

import re
from dataclasses import dataclass
from typing import Any

from ..shared.models import Claim


@dataclass
class ClaimCluster:
    """A cluster of related claims."""

    theme_id: str
    theme_name: str
    claim_ids: list[str]
    claim_texts: list[str]
    consensus: str = "unknown"
    agreement_count: int = 0
    conflict_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme_id": self.theme_id,
            "theme_name": self.theme_name,
            "claim_ids": self.claim_ids,
            "claim_texts": self.claim_texts,
            "consensus": self.consensus,
            "agreement_count": self.agreement_count,
            "conflict_count": self.conflict_count,
        }


class ThematicClusterer:
    """Cluster claims by theme/topic."""

    def __init__(self):
        self.keyword_themes = {
            "accuracy": ["accuracy", "performance", "error rate", "precision", "recall", "f1"],
            "efficiency": ["efficiency", "speed", "fast", "runtime", "latency", "throughput"],
            "scalability": ["scalability", "scale", "large-scale", "million", "billion"],
            "architecture": ["architecture", "model design", "network", "transformer", "layer"],
            "data": ["dataset", "training data", "benchmark", "corpus", "data quality"],
            "generalization": ["generalization", "overfitting", "underfitting", "regularization"],
            "interpretability": ["interpretability", "explainability", "transparency", "understand"],
            "robustness": ["robustness", "adversarial", "noise", "perturbation"],
            "comparison": ["baseline", "compared", "outperform", "state-of-the-art", "sota"],
        }

    def cluster_claims(self, claims: list[Claim]) -> list[ClaimCluster]:
        """
        Cluster claims by theme.

        Args:
            claims: List of Claim objects

        Returns:
            List of ClaimCluster objects
        """
        theme_claims: dict[str, list[Claim]] = {}

        for claim in claims:
            theme_id = self._identify_theme(claim.claim_text)
            if theme_id:
                if theme_id not in theme_claims:
                    theme_claims[theme_id] = []
                theme_claims[theme_id].append(claim)

        clusters = []
        for theme_id, theme_claims_list in theme_claims.items():
            theme_name = self._get_theme_name(theme_id)

            cluster = ClaimCluster(
                theme_id=theme_id,
                theme_name=theme_name,
                claim_ids=[c.claim_id for c in theme_claims_list],
                claim_texts=[c.claim_text for c in theme_claims_list],
            )
            clusters.append(cluster)

        clusters.sort(key=lambda c: len(c.claim_ids), reverse=True)
        return clusters

    def _identify_theme(self, claim_text: str) -> str | None:
        """Identify the theme of a claim based on keywords."""
        text_lower = claim_text.lower()

        for theme_id, keywords in self.keyword_themes.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return theme_id

        return None

    def _get_theme_name(self, theme_id: str) -> str:
        """Get human-readable theme name."""
        theme_names = {
            "accuracy": "Model Accuracy & Performance",
            "efficiency": "Computational Efficiency",
            "scalability": "Scalability",
            "architecture": "Model Architecture",
            "data": "Data & Benchmarks",
            "generalization": "Generalization & Overfitting",
            "interpretability": "Interpretability & Explainability",
            "robustness": "Robustness & Adversarial",
            "comparison": "Comparison with Baselines",
        }
        return theme_names.get(theme_id, theme_id.title())


class SemanticClusterer:
    """Cluster claims using embeddings similarity (placeholder for advanced implementation)."""

    def __init__(self):
        self.embedding_cache: dict[str, list[float]] = {}

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding for text (placeholder - returns random vector)."""
        import hashlib

        text_hash = hashlib.md5(text.encode()).digest()

        vec = [b / 255.0 for b in text_hash[:32]]
        while len(vec) < 32:
            vec.extend(vec[: min(32 - len(vec), len(vec))])

        return vec[:32]

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a * norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
