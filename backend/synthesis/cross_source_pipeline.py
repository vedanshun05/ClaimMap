"""Cross-source synthesis pipeline."""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from claim_grouper import grouper
from relation_detector import detector
from consensus_scorer import scorer

logger = logging.getLogger(__name__)


class CrossSourcePipeline:
    """Orchestrates cross-source synthesis of claims."""

    def __init__(self, relation_detector=None):
        """
        Initialize pipeline.

        Args:
            relation_detector: Optional RelationDetector instance
        """
        self.grouper = grouper
        self.detector = relation_detector or detector
        self.scorer = scorer

    async def run_async(self, claims: list[dict]) -> dict:
        """
        Run complete synthesis pipeline on claims (async, concurrent).

        Uses async relation detection for concurrent LLM calls across topics.

        Args:
            claims: List of claim dictionaries

        Returns:
            Synthesis result dict with topics, consensus, conflicts, gaps
        """
        if not claims:
            return {
                "topics": [],
                "areas_of_consensus": [],
                "areas_of_conflict": [],
                "evidence_gaps": [],
                "total_papers": len(set(c.get("paper_id") for c in claims)),
                "total_claims": 0
            }

        claim_groups = self.grouper.group_by_topic(claims)

        topics = []
        areas_of_consensus = []
        areas_of_conflict = []

        for topic_id, topic_claims in claim_groups.items():
            relations = await self.detector.compare_group_async(topic_claims)

            consensus = self.scorer.score_topic(relations, topic_claims)

            topic_name = self.grouper.get_topic_name(topic_id)

            topic_data = {
                "topic": topic_name,
                "claims": topic_claims,
                "relations": relations,
                "consensus": consensus
            }
            topics.append(topic_data)

            if consensus["agreement_ratio"] >= 0.6:
                areas_of_consensus.append(
                    f"{topic_name}: {consensus['agreement_ratio']*100:.0f}% agreement across {consensus['total_claims']} claims"
                )

            if consensus["has_conflict"]:
                areas_of_conflict.append(
                    f"{topic_name}: Contradicting claims detected"
                )

        evidence_gaps = self.scorer.identify_gaps(claim_groups)

        unique_papers = len(set(c.get("paper_id") for c in claims))

        return {
            "topics": topics,
            "areas_of_consensus": areas_of_consensus,
            "areas_of_conflict": areas_of_conflict,
            "evidence_gaps": evidence_gaps,
            "total_papers": unique_papers,
            "total_claims": len(claims)
        }

    def run(self, claims: list[dict]) -> dict:
        """
        Synchronous run — delegates to run_async.

        When called from asyncio.to_thread (as in the routers), this runs
        in a worker thread and creates a fresh event loop for async LLM calls.
        """
        return asyncio.run(self.run_async(claims))


pipeline = CrossSourcePipeline()
