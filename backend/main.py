"""FastAPI main application."""

import os
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


@app.get("/api/debug")
async def debug():
    """Debug endpoint to inspect environment variables and test LLM connectivity."""
    from openai import AsyncOpenAI

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENCODE_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")

    llm_test = None
    test_error = None

    if api_key:
        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=default_model,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                temperature=0.1,
                timeout=15.0,
            )
            llm_test = response.choices[0].message.content
        except Exception as e:
            test_error = str(e)

    return {
        "default_model": default_model,
        "api_key_present": bool(api_key),
        "llm_test": llm_test,
        "test_error": test_error,
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
