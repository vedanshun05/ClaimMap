"""Claims router - handles claim extraction with async parallel processing, dedup, and validation."""

import sys
import hashlib
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.claim import Claim, ClaimExtractionResponse
from database import paper_repo
from extraction.extractor import extract_claims_async, _extract_from_section_async, MIN_SECTION_LENGTH, MAX_SECTIONS_PER_PAPER

router = APIRouter(prefix="/api", tags=["claims"])


def _claim_hash(paper_id: str, page_number: int, claim_text: str) -> str:
    normalized = claim_text.lower().strip()
    return hashlib.md5(f"{paper_id}|{page_number}|{normalized}".encode()).hexdigest()


def _deduplicate_claims(claims: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for claim in claims:
        h = _claim_hash(
            claim.get("paper_id", ""),
            claim.get("page_number", 0),
            claim.get("text", "")
        )
        if h not in seen:
            seen.add(h)
            deduped.append(claim)
    return deduped


@router.get("/papers/{paper_id}/claims", response_model=list[dict])
async def get_claims(paper_id: str) -> list[dict]:
    claims = paper_repo.get_claims(paper_id)
    return claims


@router.post("/papers/{paper_id}/extract", response_model=ClaimExtractionResponse)
async def extract_claims(paper_id: str) -> ClaimExtractionResponse:
    """Extract claims from a paper using async parallel LLM calls."""
    paper = paper_repo.get(paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_repo.clear_claims(paper_id)

    sections = [
        {
            "heading": s.heading,
            "content": s.content,
            "page_number": s.page_number
        }
        for s in paper.sections
    ]

    raw_claims = await extract_claims_async(paper_id, sections)

    from extraction import validator
    source_sections = {s.heading: s.content for s in paper.sections}
    valid_claims, invalid_claims = validator.filter_valid(raw_claims, source_sections)

    deduped_claims = _deduplicate_claims(valid_claims)

    saved_claims = []
    for claim in deduped_claims:
        saved = paper_repo.save_claim(paper_id, claim)
        saved_claims.append(saved)

    duplicate_count = len(valid_claims) - len(deduped_claims)

    return ClaimExtractionResponse(
        paper_id=paper_id,
        claims=saved_claims,
        extraction_success=True,
        message=(
            f"Extracted {len(deduped_claims)} unique claims "
            f"({len(invalid_claims)} invalid, {duplicate_count} duplicates removed)"
        )
    )


@router.get("/papers/{paper_id}/extract/stream")
async def extract_claims_stream(paper_id: str):
    """Stream extraction progress as SSE events."""
    paper = paper_repo.get(paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_repo.clear_claims(paper_id)

    sections = [
        {
            "heading": s.heading,
            "content": s.content,
            "page_number": s.page_number
        }
        for s in paper.sections
    ]

    candidates = [
        s for s in sections
        if s["heading"] and s["content"] and len(s["content"]) >= MIN_SECTION_LENGTH
    ]
    candidates.sort(key=lambda x: len(x["content"]), reverse=True)
    candidates = candidates[:MAX_SECTIONS_PER_PAPER]

    async def event_generator():
        yield f"data: {json.dumps({'type': 'start', 'total_sections': len(candidates)})}\n\n"

        all_claims = []
        for i, section in enumerate(candidates):
            yield f"data: {json.dumps({'type': 'progress', 'section': section['heading'], 'current': i + 1, 'total': len(candidates)})}\n\n"

            section_claims = await _extract_from_section_async(
                section_content=section["content"],
                section_name=section["heading"],
                page_number=section["page_number"]
            )

            for claim in section_claims:
                claim["paper_id"] = paper_id

            all_claims.extend(section_claims)

            yield f"data: {json.dumps({'type': 'section_done', 'section': section['heading'], 'claims_found': len(section_claims), 'total_claims_so_far': len(all_claims)})}\n\n"

        from extraction import validator
        source_sections = {s.heading: s.content for s in paper.sections}
        valid_claims, invalid_claims = validator.filter_valid(all_claims, source_sections)

        deduped_claims = _deduplicate_claims(valid_claims)

        saved_claims = []
        for claim in deduped_claims:
            saved = paper_repo.save_claim(paper_id, claim)
            saved_claims.append(saved)

        duplicate_count = len(valid_claims) - len(deduped_claims)

        yield f"data: {json.dumps({'type': 'complete', 'claims': saved_claims, 'total': len(deduped_claims), 'invalid': len(invalid_claims), 'duplicates': duplicate_count, 'message': f'Extracted {len(deduped_claims)} unique claims ({len(invalid_claims)} invalid, {duplicate_count} duplicates removed)'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/claims/all", response_model=list[dict])
async def get_all_claims() -> list[dict]:
    return paper_repo.get_all_claims()