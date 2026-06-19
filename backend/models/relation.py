"""Relation and synthesis Pydantic models."""

from typing import Optional
from pydantic import BaseModel, Field


class Relation(BaseModel):
    """Relationship between two claims."""

    id: Optional[int] = None
    claim_ids: list[str] = Field(
        ...,
        description="IDs of claims involved in this relation"
    )
    relation_type: str = Field(
        ...,
        description="Type: 'agrees', 'contradicts', 'supports', or 'gap'"
    )
    explanation: str = ""
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence score 0-1"
    )

    class Config:
        from_attributes = True


class ConsensusScore(BaseModel):
    """Consensus score for a topic."""

    topic: str = ""
    total_claims: int = 0
    agreement_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of agreeing to total claims"
    )
    has_conflict: bool = False
    evidence_strength: str = Field(
        default="thin",
        description="Strength: 'strong', 'moderate', or 'thin'"
    )

    class Config:
        from_attributes = True


class TopicGroup(BaseModel):
    """Group of claims clustered by topic."""

    topic: str
    claims: list[dict] = Field(
        default_factory=list,
        description="List of claim dicts in this topic"
    )
    relations: list[Relation] = Field(default_factory=list)
    consensus: Optional[ConsensusScore] = None

    class Config:
        from_attributes = True


class SynthesisResult(BaseModel):
    """Complete synthesis result."""

    topics: list[TopicGroup] = Field(default_factory=list)
    areas_of_consensus: list[str] = Field(default_factory=list)
    areas_of_conflict: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    total_papers: int = 0
    total_claims: int = 0

    class Config:
        from_attributes = True


class SynthesisResponse(BaseModel):
    """Response from synthesis endpoint."""

    synthesis: SynthesisResult
    success: bool
    message: str = ""
