"""
Agent 4: Cross-Source Synthesis

Group related claims across papers. Identify where sources agree,
conflict, or where evidence is thin. Surface the strength of consensus.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.config import config
from src.shared.utils import load_json, save_json, claims_from_dict, ingested_from_dict
from src.shared.models import Claim, SynthesisResult, ThemeSynthesis
from .clustering import ThematicClusterer, ClaimCluster
from .consensus import ConsensusDetector, ConflictDetector, ConsensusResult


@dataclass
class SynthesisTheme:
    """Theme with full synthesis information."""

    theme_id: str
    theme_name: str
    claim_ids: list[str]
    consensus: str
    agreement_count: int
    conflict_count: int
    summary: str
    consensus_details: dict = field(default_factory=dict)

    def to_theme_synthesis(self) -> ThemeSynthesis:
        return ThemeSynthesis(
            theme_id=self.theme_id,
            theme_name=self.theme_name,
            claim_ids=self.claim_ids,
            consensus=self.consensus,
            agreement_count=self.agreement_count,
            conflict_count=self.conflict_count,
            summary=self.summary,
        )


class CrossSourceSynthesisAgent:
    """
    Agent responsible for synthesizing claims across multiple sources.

    Groups related claims, identifies consensus/conflict,
    and detects evidence gaps.
    """

    def __init__(self):
        self.clusterer = ThematicClusterer()
        self.consensus_detector = ConsensusDetector()
        self.conflict_detector = ConflictDetector()

    def synthesize(
        self,
        claims: list[dict] | None = None,
        papers: list[dict] | None = None,
    ) -> SynthesisResult:
        """
        Synthesize claims across sources.

        Args:
            claims: List of claim dicts. If None, loads from data store.
            papers: List of paper dicts for metadata. If None, loads from data store.

        Returns:
            SynthesisResult object
        """
        if claims is None:
            filepath = config.data_dir / config.extracted_claims_file
            data = load_json(filepath)
            claims = claims_from_dict(data)

        if papers is None:
            filepath = config.data_dir / config.ingested_papers_file
            data = load_json(filepath)
            papers = ingested_from_dict(data)

        print(f"[Agent 4] Synthesizing {len(claims)} claims from {len(papers)} papers...")

        paper_dict = {p.paper_id: p.to_dict() if hasattr(p, 'to_dict') else p for p in papers}

        clusters = self.clusterer.cluster_claims(claims)
        print(f"[Agent 4] Created {len(clusters)} theme clusters")

        themes = []
        areas_of_consensus = []
        areas_of_conflict = []
        evidence_gaps = []

        for cluster in clusters:
            theme_synthesis = self._synthesize_cluster(cluster, paper_dict)

            themes.append(theme_synthesis.to_theme_synthesis())

            if theme_synthesis.consensus in ["strong", "moderate"]:
                areas_of_consensus.append(theme_synthesis.summary)
            elif theme_synthesis.consensus == "conflicting":
                areas_of_conflict.append(theme_synthesis.summary)
            elif len(cluster.claim_ids) < 2:
                evidence_gaps.append(f"{theme_synthesis.theme_name}: Single-source claims only")

        print(f"[Agent 4] Consensus areas: {len(areas_of_consensus)}")
        print(f"[Agent 4] Conflict areas: {len(areas_of_conflict)}")
        print(f"[Agent 4] Evidence gaps: {len(evidence_gaps)}")

        return SynthesisResult(
            themes=themes,
            areas_of_consensus=areas_of_consensus,
            areas_of_conflict=areas_of_conflict,
            evidence_gaps=evidence_gaps,
        )

    def _synthesize_cluster(
        self,
        cluster: ClaimCluster,
        paper_dict: dict,
    ) -> SynthesisTheme:
        """Synthesize a single theme cluster."""
        cluster_claims = []
        for cid in cluster.claim_ids:
            for c_dict in load_json(config.data_dir / config.extracted_claims_file):
                if c_dict["claim_id"] == cid:
                    cluster_claims.append(Claim(**c_dict))
                    break

        consensus_result = self.consensus_detector.analyze_consensus(cluster_claims, paper_dict)

        conflicts = self.conflict_detector.find_conflicts(cluster_claims)

        return SynthesisTheme(
            theme_id=cluster.theme_id,
            theme_name=cluster.theme_name,
            claim_ids=cluster.claim_ids,
            consensus=consensus_result.consensus,
            agreement_count=consensus_result.agreement_count,
            conflict_count=consensus_result.conflict_count + len(conflicts),
            summary=consensus_result.summary,
            consensus_details={
                "supporting_papers": consensus_result.supporting_papers,
                "conflicts": conflicts,
            },
        )

    def save_synthesis(self, synthesis: SynthesisResult) -> Path:
        """Save synthesis to the data directory."""
        filepath = config.data_dir / config.synthesis_file
        save_json(synthesis.to_dict(), filepath)
        print(f"[Agent 4] Saved synthesis to {filepath}")
        return filepath


def main():
    """CLI entry point for Agent 4."""
    agent = CrossSourceSynthesisAgent()
    synthesis = agent.synthesize()
    agent.save_synthesis(synthesis)

    print("\n[Agent 4] Synthesis Summary:")
    print(f"  Themes: {len(synthesis.themes)}")
    print(f"  Areas of consensus: {len(synthesis.areas_of_consensus)}")
    print(f"  Areas of conflict: {len(synthesis.areas_of_conflict)}")
    print(f"  Evidence gaps: {len(synthesis.evidence_gaps)}")


if __name__ == "__main__":
    main()
