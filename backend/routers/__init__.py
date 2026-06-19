"""Routers package."""

from .discovery import router as discovery_router
from .claims import router as claims_router
from .synthesis_router import router as synthesis_router
from .brief_router import router as brief_router

__all__ = [
    "discovery_router",
    "claims_router",
    "synthesis_router",
    "brief_router",
]
