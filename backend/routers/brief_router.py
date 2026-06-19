"""Brief router - handles research brief generation and export (non-blocking)."""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter
from pydantic import BaseModel

from models.research_brief import BriefGenerationResponse, ExportRequest, ExportResponse
from database import paper_repo
from synthesis import pipeline
from brief import generator

router = APIRouter(prefix="/api", tags=["brief"])


class GenerateBriefRequest(BaseModel):
    query: str = "Research on deep learning"


@router.get("/brief", response_model=BriefGenerationResponse)
async def get_brief(query: str = "Research on deep learning") -> BriefGenerationResponse:
    """Generate a research brief (cached, non-blocking)."""
    papers = paper_repo.list_all()
    claims = paper_repo.get_all_claims()

    if not papers:
        return BriefGenerationResponse(
            brief={
                "query": query,
                "papers_analyzed": 0,
                "executive_summary": "No papers available. Ingest papers and extract claims first.",
                "themes": [],
                "areas_of_consensus": [],
                "areas_of_conflict": [],
                "open_questions": [],
                "recommended_next_papers": [],
            },
            success=False,
            message="No papers found in database",
        )

    claim_count = len(claims)
    
    # Generate stable cache key based on query and sorted claim IDs
    import hashlib
    claim_ids = sorted(str(c.get("id", "")) for c in claims)
    claims_hash = hashlib.md5("".join(claim_ids).encode()).hexdigest()
    cache_key = f"{query}:{claims_hash}"

    brief = paper_repo.get_brief_cache(cache_key)
    if not brief:
        synthesis_result = await pipeline.run_async(claims)
        papers_dict = [p.model_dump() for p in papers]
        brief = await generator.generate_async(query, papers_dict, claims, synthesis_result)
        paper_repo.save_brief_cache(cache_key, brief, claim_count)

    return BriefGenerationResponse(
        brief=brief,
        success=True,
        message=f"Generated brief for {brief['papers_analyzed']} papers",
    )


@router.post("/brief/export", response_model=ExportResponse)
async def export_brief(
    request: ExportRequest,
    query: str = "Research on deep learning",
) -> ExportResponse:
    """Export the research brief in specified format (non-blocking)."""
    papers = paper_repo.list_all()
    claims = paper_repo.get_all_claims()

    if not papers:
        return ExportResponse(
            content="No papers available",
            format=request.format,
            success=False,
            message="No papers found in database",
        )

    synthesis_result = await pipeline.run_async(claims)
    papers_dict = [p.model_dump() for p in papers]
    brief = await generator.generate_async(query, papers_dict, claims, synthesis_result)

    if request.format == "bibtex":
        content = generator.export_bibtex(papers_dict)
    elif request.format == "json":
        content = json.dumps(brief, indent=2)
    else:
        content = generator.export_markdown(brief, papers_dict)

    return ExportResponse(
        content=content,
        format=request.format,
        success=True,
        message=f"Exported brief as {request.format}",
    )