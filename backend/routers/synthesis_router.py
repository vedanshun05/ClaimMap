"""Synthesis router - handles cross-source synthesis with caching."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter

from models.relation import SynthesisResponse
from database import paper_repo
from synthesis import pipeline

router = APIRouter(prefix="/api", tags=["synthesis"])

@router.get("/synthesis", response_model=SynthesisResponse)
async def get_synthesis() -> SynthesisResponse:
    """Run cross-source synthesis on all claims (cached, non-blocking)."""
    claims = paper_repo.get_all_claims()

    if not claims:
        return SynthesisResponse(
            synthesis={
                "topics": [],
                "areas_of_consensus": [],
                "areas_of_conflict": [],
                "evidence_gaps": [],
                "total_papers": 0,
                "total_claims": 0,
            },
            success=True,
            message="No claims found. Extract claims from papers first.",
        )

    claim_count = len(claims)
    
    # Generate stable claims hash based on sorted claim IDs
    import hashlib
    claim_ids = sorted(str(c.get("id", "")) for c in claims)
    claims_hash = hashlib.md5("".join(claim_ids).encode()).hexdigest()

    result = paper_repo.get_synthesis_cache(claims_hash)
    if not result:
        result = await pipeline.run_async(claims)
        paper_repo.save_synthesis_cache(claims_hash, result, claim_count)

    return SynthesisResponse(
        synthesis=result,
        success=True,
        message=f"Synthesized {result['total_claims']} claims from {result['total_papers']} papers",
    )