"""Synthesis Engine module - Cross-source analysis, clustering, and consensus detection."""

from .clustering import ThematicClusterer, SemanticClusterer, ClaimCluster
from .consensus import ConsensusDetector, ConflictDetector, ConsensusResult
from .agent import CrossSourceSynthesisAgent, SynthesisTheme

__all__ = [
    "ThematicClusterer",
    "SemanticClusterer",
    "ClaimCluster",
    "ConsensusDetector",
    "ConflictDetector",
    "ConsensusResult",
    "CrossSourceSynthesisAgent",
    "SynthesisTheme",
]
