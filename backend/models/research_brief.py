"""Research Brief Pydantic models."""

from typing import Optional
from pydantic import BaseModel, Field


class ThemeSummary(BaseModel):
    """Summary of a theme in the research brief."""

    theme: str
    summary: str = ""
    supporting_claim_ids: list[str] = Field(default_factory=list)
    consensus_level: str = Field(
        default="thin",
        description="Level: 'strong', 'moderate', or 'thin'"
    )

    class Config:
        from_attributes = True


class ResearchBrief(BaseModel):
    """Complete research brief."""

    query: str = ""
    papers_analyzed: int = 0
    executive_summary: str = ""
    themes: list[ThemeSummary] = Field(default_factory=list)
    areas_of_consensus: list[str] = Field(default_factory=list)
    areas_of_conflict: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_next_papers: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class BriefGenerationResponse(BaseModel):
    """Response from brief generation endpoint."""

    brief: ResearchBrief
    success: bool
    message: str = ""


class ExportRequest(BaseModel):
    """Request to export brief."""

    format: str = Field(
        default="md",
        description="Export format: 'md', 'bibtex', or 'json'"
    )


class ExportResponse(BaseModel):
    """Response containing exported content."""

    content: str
    format: str
    success: bool
    message: str = ""
