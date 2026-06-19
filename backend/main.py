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


@app.get("/api/debug")
async def debug():
    """Temporary debug endpoint to inspect environment variables and test LLM connectivity."""
    import os
    import litellm
    from pathlib import Path
    
    # Try to see if keys are in environment or loaded
    nvidia_key = os.getenv("NVIDIA_NIM_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "nvidia_nim/meta/llama-3.1-8b-instruct")

    
    test_result = None
    test_error = None
    
    try:
        # Re-initialize key mapping as in extractor
        api_key = nvidia_key or gemini_key
        if api_key:
            os.environ["NVIDIA_API_KEY"] = api_key
            
        response = await litellm.acompletion(
            model=default_model,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.1,
            timeout=15.0
        )
        test_result = response.choices[0].message.content
    except Exception as e:
        test_error = str(e)
        
    return {
        "default_model": default_model,
        "nvidia_key_present": bool(nvidia_key),
        "gemini_key_present": bool(gemini_key),
        "nvidia_key_prefix": nvidia_key[:8] if nvidia_key else None,
        "gemini_key_prefix": gemini_key[:8] if gemini_key else None,
        "test_result": test_result,
        "test_error": test_error
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
