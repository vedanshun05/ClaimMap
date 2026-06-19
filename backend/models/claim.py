"""Claim Pydantic model."""

from typing import Optional
from pydantic import BaseModel, Field


class Claim(BaseModel):
    """Extracted claim with provenance and type classification."""

    id: Optional[int] = None
    paper_id: str
    text: str = Field(..., description="The claim text")
    claim_type: str = Field(
        ...,
        description="Type: 'finding', 'hypothesis', or 'limitation'"
    )
    source_section: str = ""
    source_sentence: str = Field(
        ...,
        description="The exact sentence from the source text"
    )
    page_number: int = 0
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score 0-1"
    )
    is_validated: bool = Field(
        default=False,
        description="Whether the claim has been validated against source"
    )

    class Config:
        from_attributes = True


class ClaimExtractionResponse(BaseModel):
    """Response from claim extraction."""

    paper_id: str
    claims: list[Claim]
    extraction_success: bool
    message: str = ""


class ClaimTypeStats(BaseModel):
    """Statistics about claim types in a paper."""

    findings: int = 0
    hypotheses: int = 0
    limitations: int = 0
    total: int = 0
