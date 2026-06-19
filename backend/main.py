"""FastAPI main application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import discovery_router, claims_router, synthesis_router, brief_router

app = FastAPI(
    title="AI Research Synthesis Engine API",
    description="API for transforming academic papers into coherent research briefs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discovery_router)
app.include_router(claims_router)
app.include_router(synthesis_router)
app.include_router(brief_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Research Synthesis Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "discovery": "/api/search, /api/ingest/{paper_id}, /api/papers",
            "claims": "/api/papers/{paper_id}/claims, /api/papers/{paper_id}/extract",
            "synthesis": "/api/synthesis",
            "brief": "/api/brief, /api/brief/export"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
