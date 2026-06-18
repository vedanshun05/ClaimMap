"""Consensus scorer - calculates consensus scores for topics."""

from typing import Optional


class ConsensusScorer:
    """Calculates consensus scores for claim groups."""

    def score_topic(
        self,
        relations: list[dict],
        claims: list[dict]
    ) -> dict:
        """
        Calculate consensus score for a topic group.

        Args:
            relations: List of relation dicts
            claims: List of claims in the topic

        Returns:
            ConsensusScore dict
        """
        total_claims = len(claims)

        if total_claims == 0:
            return {
                "topic": "",
                "total_claims": 0,
                "agreement_ratio": 0.0,
                "has_conflict": False,
                "evidence_strength": "thin"
            }

        agrees = sum(1 for r in relations if r.get("relation_type") == "agrees")
        supports = sum(1 for r in relations if r.get("relation_type") == "supports")
        contradicts = sum(1 for r in relations if r.get("relation_type") == "contradicts")

        total_relations = len(relations) if relations else 1
        agreement_ratio = (agrees + supports) / total_relations

        has_conflict = contradicts > 0

        if total_claims > 5 and agreement_ratio >= 0.7:
            evidence_strength = "strong"
        elif total_claims >= 3 and agreement_ratio >= 0.5:
            evidence_strength = "moderate"
        else:
            evidence_strength = "thin"

        return {
            "total_claims": total_claims,
            "agreement_ratio": round(agreement_ratio, 2),
            "has_conflict": has_conflict,
            "evidence_strength": evidence_strength
        }

    def identify_gaps(self, claims_by_topic: dict[str, list[dict]]) -> list[str]:
        """
        Identify evidence gaps based on claim distribution.

        Args:
            claims_by_topic: Dict mapping topic to list of claims

        Returns:
            List of gap descriptions
        """
        gaps = []

        for topic, claims in claims_by_topic.items():
            if len(claims) < 2:
                topic_name = topic.replace("_", " ").title()
                gaps.append(f"{topic_name}: Limited evidence (only {len(claims)} claim(s))")

        return gaps


scorer = ConsensusScorer()
