"""Paper and Section Pydantic models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Section(BaseModel):
    """A section of a paper with heading, content, and page number."""

    id: Optional[int] = None
    paper_id: str
    heading: str = ""
    content: str = ""
    page_number: int = 0

    class Config:
        from_attributes = True


class Paper(BaseModel):
    """Paper with metadata and sections."""

    id: str = Field(..., description="Unique paper identifier (e.g., arXiv:1706.03762)")
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: int = 0
    abstract: str = ""
    source: str = Field(..., description="Source: 'arxiv' or 'semantic_scholar'")
    source_id: str = ""
    pdf_path: Optional[str] = None
    sections: list[Section] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaperSearchResult(BaseModel):
    """Paper from search result with relevance score."""

    paper_id: str
    title: str
    authors: list[str]
    year: int
    abstract: str
    url: str
    source: str
    relevance_score: float = 0.0
    citation_count: int = 0


class SearchRequest(BaseModel):
    """Request to search for papers."""

    query: str
    max_results: int = 10


class SearchResponse(BaseModel):
    """Response containing search results."""

    papers: list[PaperSearchResult]
    total: int


class IngestRequest(BaseModel):
    """Request to ingest a paper."""

    paper_id: str
    pdf_url: Optional[str] = None
