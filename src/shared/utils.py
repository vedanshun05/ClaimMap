"""Utilities for the research synthesis pipeline."""

import json
from pathlib import Path
from typing import TypeVar, Type

from .models import PaperMetadata, IngestedPaper, Claim, SynthesisResult, ThemeSynthesis

T = TypeVar("T")


def load_json(filepath: Path) -> list[dict]:
    """Load JSON file, returns empty list if file doesn't exist."""
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: list[dict], filepath: Path) -> None:
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def papers_from_dict(data: list[dict]) -> list[PaperMetadata]:
    """Convert list of dicts to PaperMetadata objects."""
    return [PaperMetadata(**d) for d in data]


def ingested_from_dict(data: list[dict]) -> list[IngestedPaper]:
    """Convert list of dicts to IngestedPaper objects."""
    result = []
    for d in data:
        d_copy = d.copy()
        d_copy.setdefault("authors", [])
        result.append(IngestedPaper(**d_copy))
    return result


def claims_from_dict(data: list[dict]) -> list[Claim]:
    """Convert list of dicts to Claim objects."""
    return [Claim(**d) for d in data]


def synthesis_from_dict(data: dict) -> SynthesisResult:
    """Convert dict to SynthesisResult object."""
    themes = [ThemeSynthesis(**t) for t in data.get("themes", [])]
    return SynthesisResult(
        themes=themes,
        areas_of_consensus=data.get("areas_of_consensus", []),
        areas_of_conflict=data.get("areas_of_conflict", []),
        evidence_gaps=data.get("evidence_gaps", []),
    )


def get_output_path(base_dir: Path, filename: str, create: bool = True) -> Path:
    """Get path for output files."""
    if create:
        base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / filename
