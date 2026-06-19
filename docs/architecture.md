# Architecture

## Overview

The AI Research Synthesis Engine transforms academic papers into coherent, traceable research briefs through a 5-stage pipeline.

## System Architecture

```
User Query/PDFs
    │
    ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Paper Discovery │────▶│ Doc Ingestion    │────▶│ Claim Extraction │
│  (arXiv, S2,     │     │ (PDF parsing,    │     │ (LLM: findings,  │
│   PDF upload)    │     │  metadata)       │     │  hypotheses,     │
│                  │     │                  │     │  limitations)    │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Export         │◀────│ Research Brief   │◀────│ Cross-Source     │
│  (MD, BibTeX,   │     │ + Citations      │     │ Synthesis        │
│   PDF)          │     │ (structured doc) │     │ (agree/conflict) │
└─────────────────┘     └──────────────────┘     └──────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Lightweight database for paper/claim storage
- **PyMuPDF** - PDF text extraction
- **litellm** - Unified interface for LLM providers (NVIDIA NIM, Gemini)

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **Axios** - HTTP client

### APIs
- **arXiv** - Academic paper search (via `arxiv` Python library)
- **Semantic Scholar** - Paper metadata enrichment

## Module Descriptions

### 1. Paper Discovery (`backend/routers/discovery.py`)
Handles searching academic sources and ranking results.

**Endpoints:**
- `POST /api/search` - Search arXiv + Semantic Scholar
- `POST /api/ingest/{paper_id}` - Download and parse PDF
- `GET /api/papers` - List all ingested papers
- `GET /api/papers/{paper_id}` - Get specific paper

**Key Features:**
- TF-IDF style relevance scoring
- Deduplication by title
- PDF download and section extraction

### 2. Claim Extraction (`backend/extraction/`)
Extracts factual claims from paper sections using LLM.

**Components:**
- `extractor.py` - LLM-powered claim extraction
- `validator.py` - Validates claims against source text

**Claim Types:**
- `finding` - Proven results
- `hypothesis` - Proposed but unproven
- `limitation` - Acknowledged weaknesses

### 3. Cross-Source Synthesis (`backend/synthesis/`)
Groups claims and identifies consensus/conflict.

**Components:**
- `claim_grouper.py` - Groups claims by topic
- `relation_detector.py` - Compares claim pairs
- `consensus_scorer.py` - Calculates agreement scores
- `cross_source_pipeline.py` - Orchestrates synthesis

### 4. Brief Generation (`backend/brief/`)
Creates structured research briefs.

**Components:**
- `generator.py` - LLM-powered brief generation
- `citation_formatter.py` - APA, BibTeX, inline formats

### 5. Database (`backend/database/`)
SQLite repository for persistent storage.

**Tables:**
- `papers` - Paper metadata
- `sections` - Paper sections with page numbers
- `claims` - Extracted claims with validation status

## Data Flow

1. **Discovery**: User searches → arXiv/S2 results ranked
2. **Ingestion**: Selected paper → PDF downloaded → parsed into sections
3. **Extraction**: Sections → LLM extracts claims → validated against source
4. **Synthesis**: Claims → grouped by topic → relations detected → consensus scored
5. **Brief**: Synthesis + claims → LLM generates structured brief → exported

## API Contract

All modules agree on Pydantic models as the API contract:

```python
Paper(id, title, authors, year, abstract, source, sections[])
Section(id, paper_id, heading, content, page_number)
Claim(id, paper_id, text, claim_type, source_section, source_sentence, confidence, is_validated)
```

## Hallucination Prevention

Claims must cite verbatim source text. The validator:
1. Extracts candidate claims via LLM
2. Checks if `source_sentence` exists in original section text
3. Rejects claims without exact match (>90% substring match)

## Rate Limiting

- arXiv: 1 req/3 seconds
- Gemini: 60 req/min
- NVIDIA NIM: Variable per tier

Implementation uses exponential backoff and in-memory caching.
