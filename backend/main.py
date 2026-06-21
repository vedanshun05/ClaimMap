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

    opencode_key = os.getenv("OPENCODE_API_KEY")
    nvidia_key = os.getenv("NVIDIA_NIM_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "openai/deepseek-v4-flash-free")

    opencode_test = None
    nvidia_test = None
    test_error = None

    # Test OpenCode Zen
    if opencode_key:
        try:
            response = await litellm.acompletion(
                model="openai/deepseek-v4-flash-free",
                api_base="https://opencode.ai/zen/v1",
                api_key=opencode_key,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                temperature=0.1,
                timeout=15.0
            )
            opencode_test = response.choices[0].message.content
        except Exception as e:
            test_error = str(e)

    # Test NVIDIA fallback (backward compat)
    if nvidia_key and not opencode_test:
        try:
            os.environ["NVIDIA_API_KEY"] = nvidia_key
            response = await litellm.acompletion(
                model=default_model,
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.1,
                timeout=15.0
            )
            nvidia_test = response.choices[0].message.content
        except Exception as e:
            test_error = test_error or str(e)

    return {
        "default_model": default_model,
        "opencode_key_present": bool(opencode_key),
        "nvidia_key_present": bool(nvidia_key),
        "gemini_key_present": bool(gemini_key),
        "opencode_key_prefix": opencode_key[:8] + "..." if opencode_key else None,
        "opencode_test": opencode_test,
        "nvidia_test": nvidia_test,
        "test_error": test_error
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
