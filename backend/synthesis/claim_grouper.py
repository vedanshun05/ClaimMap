"""Claim grouper - groups claims by topic/theme."""

import json
import re
from typing import Optional


class ClaimGrouper:
    """Groups claims by topic using keyword matching or LLM."""

    TOPIC_KEYWORDS = {
        "architecture": [
            "architecture", "model", "network", "layer", "transformer", "encoder", "decoder",
            "attention", "neural", "deep", "embedding", "weight", "parameter"
        ],
        "training": [
            "train", "training", "optimizer", "learning rate", "batch", "epoch",
            "gradient", "overfit", "regularization", "dropout", "converge"
        ],
        "performance": [
            "accuracy", "performance", "benchmark", "result", "score", " BLEU", " F1",
            "perplexity", "state-of-the-art", "SOTA", "improve"
        ],
        "data": [
            "dataset", "data", "corpus", "example", "sample", "token", "sequence",
            "pre-training", "fine-tuning", "supervised"
        ],
        "application": [
            "apply", "task", "translation", "QA", "question answering", "classification",
            "generation", "summarization", "downstream", "NMT"
        ],
        "limitation": [
            "limit", "challenge", "problem", "issue", "cannot", "unable", "fail",
            "weakness", "difficult", "expensive", "computational"
        ]
    }

    def __init__(self, use_llm: bool = False):
        """
        Initialize claim grouper.

        Args:
            use_llm: Whether to use LLM for topic assignment (not implemented yet)
        """
        self.use_llm = use_llm

    def assign_topic(self, claim_text: str) -> Optional[str]:
        """
        Assign a topic to a claim based on keywords.

        Args:
            claim_text: The claim text

        Returns:
            Topic name or None if no match
        """
        claim_lower = claim_text.lower()

        best_topic = None
        best_score = 0

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in claim_lower)
            if score > best_score:
                best_score = score
                best_topic = topic

        if best_score > 0:
            return best_topic

        return None

    def group_by_topic(self, claims: list[dict]) -> dict[str, list[dict]]:
        """
        Group claims by assigned topic.

        Args:
            claims: List of claim dictionaries

        Returns:
            Dict mapping topic name to list of claims
        """
        groups: dict[str, list[dict]] = {}

        for claim in claims:
            topic = self.assign_topic(claim.get("text", ""))
            if topic:
                if topic not in groups:
                    groups[topic] = []
                groups[topic].append(claim)

        return groups

    def get_topic_name(self, topic_id: str) -> str:
        """
        Get human-readable name for a topic.

        Args:
            topic_id: Topic identifier

        Returns:
            Human-readable topic name
        """
        names = {
            "architecture": "Model Architecture",
            "training": "Training & Optimization",
            "performance": "Performance & Benchmarks",
            "data": "Data & Pre-training",
            "application": "Applications & Tasks",
            "limitation": "Limitations & Challenges"
        }
        return names.get(topic_id, topic_id.title())


grouper = ClaimGrouper()
