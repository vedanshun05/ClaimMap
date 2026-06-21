"""Consensus and conflict detection for claims."""

from dataclasses import dataclass
from typing import Any

from ..shared.models import Claim


@dataclass
class ConsensusResult:
    """Result of consensus analysis."""

    theme_id: str
    theme_name: str
    consensus: str
    agreement_count: int
    conflict_count: int
    supporting_papers: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme_id": self.theme_id,
            "theme_name": self.theme_name,
            "consensus": self.consensus,
            "agreement_count": self.agreement_count,
            "conflict_count": self.conflict_count,
            "supporting_papers": self.supporting_papers,
            "summary": self.summary,
        }


class ConsensusDetector:
    """Detect consensus and conflicts across claims."""

    agreement_indicators = [
        "confirm",
        "support",
        "consistent",
        "agree",
        "validate",
        "verify",
        "demonstrate",
        "show",
        "prove",
        "found",
        "observe",
        "report",
        "achieve",
        "improve",
        "outperform",
    ]

    disagreement_indicators = [
        "contradict",
        "conflict",
        "disagree",
        "inconsistent",
        "challenge",
        "question",
        "oppose",
        "whereas",
        "however",
        "although",
        "but",
        "despite",
        "contrary",
    ]

    def analyze_consensus(
        self,
        claims: list[Claim],
        papers: dict[str, dict],
    ) -> ConsensusResult:
        """
        Analyze consensus for a group of claims.

        Args:
            claims: List of claims to analyze
            papers: Dict mapping paper_id to paper metadata

        Returns:
            ConsensusResult
        """
        if not claims:
            return ConsensusResult(
                theme_id="unknown",
                theme_name="Unknown",
                consensus="unknown",
                agreement_count=0,
                conflict_count=0,
                supporting_papers=[],
                summary="No claims to analyze.",
            )

        claim_texts = [c.claim_text for c in claims]
        supporting_paper_ids = list(set(c.paper_id for c in claims))

        agreement_count = sum(1 for text in claim_texts if self._indicates_agreement(text))
        disagreement_count = sum(1 for text in claim_texts if self._indicates_disagreement(text))

        if disagreement_count > 0 and agreement_count > disagreement_count:
            consensus = "conflicting"
        elif agreement_count > 0 and disagreement_count == 0:
            consensus = "strong" if agreement_count >= 3 else "moderate"
        elif disagreement_count > agreement_count:
            consensus = "conflicting"
        else:
            consensus = "weak"

        summary = self._generate_summary(consensus, agreement_count, disagreement_count, len(claims))

        return ConsensusResult(
            theme_id=claims[0].claim_id.split("_")[0] if claims else "unknown",
            theme_name="Theme",
            consensus=consensus,
            agreement_count=agreement_count,
            conflict_count=disagreement_count,
            supporting_papers=supporting_paper_ids,
            summary=summary,
        )

    def _indicates_agreement(self, text: str) -> bool:
        """Check if text indicates agreement/support."""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.agreement_indicators)

    def _indicates_disagreement(self, text: str) -> bool:
        """Check if text indicates disagreement/conflict."""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.disagreement_indicators)

    def _generate_summary(
        self,
        consensus: str,
        agreement: int,
        disagreement: int,
        total: int,
    ) -> str:
        """Generate human-readable summary."""
        if consensus == "strong":
            return f"Strong consensus with {agreement} supporting claims from {total} total."
        elif consensus == "moderate":
            return f"Moderate consensus with {agreement} supporting claims."
        elif consensus == "weak":
            return f"Weak consensus with limited supporting evidence ({agreement}/{total})."
        elif consensus == "conflicting":
            return f"Conflicting evidence: {agreement} supporting vs {disagreement} contradicting claims."
        else:
            return "Insufficient evidence to determine consensus."


class ConflictDetector:
    """Detect specific conflicts between claims."""

    def find_conflicts(self, claims: list[Claim]) -> list[dict[str, Any]]:
        """
        Find conflicting claims.

        Args:
            claims: List of claims to analyze

        Returns:
            List of conflict dicts
        """
        conflicts = []

        for i, claim1 in enumerate(claims):
            for claim2 in claims[i + 1 :]:
                if self._are_conflicting(claim1, claim2):
                    conflicts.append({
                        "claim1_id": claim1.claim_id,
                        "claim1_text": claim1.claim_text[:100],
                        "claim2_id": claim2.claim_id,
                        "claim2_text": claim2.claim_text[:100],
                        "paper1_id": claim1.paper_id,
                        "paper2_id": claim2.paper_id,
                    })

        return conflicts

    def _are_conflicting(self, claim1: Claim, claim2: Claim) -> bool:
        """Check if two claims are contradictory."""
        if claim1.paper_id == claim2.paper_id:
            return False

        text1 = claim1.claim_text.lower()
        text2 = claim2.claim_text.lower()

        contradictions = [
            ("improve", "degrade"),
            ("increase", "decrease"),
            ("higher", "lower"),
            ("better", "worse"),
            ("outperform", "underperform"),
            ("significant", "insignificant"),
            ("reduce", "increase"),
        ]

        for pos, neg in contradictions:
            if (pos in text1 and neg in text2) or (neg in text1 and pos in text2):
                return True

        return False
