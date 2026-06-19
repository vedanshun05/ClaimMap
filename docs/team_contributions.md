# Team Contributions

## Project: AI Research Synthesis Engine

## Overview

This document tracks individual contributions to the project. The project was developed according to the module specifications in `GenAI Group Project.md`.

---

## Module Assignments

| Member | Primary Modules | Files Created |
|--------|---------------|---------------|
| Member 1 | Paper Discovery + Document Ingestion | `backend/routers/discovery.py`, `backend/database/paper_repo.py` |
| Member 2 | Claim Extraction | `backend/extraction/extractor.py`, `backend/extraction/validator.py`, `backend/prompts/claim_extraction.py` |
| Member 3 | Cross-Source Synthesis | `backend/synthesis/claim_grouper.py`, `backend/synthesis/relation_detector.py`, `backend/synthesis/consensus_scorer.py` |
| Member 4 | FastAPI Backend + React Frontend + Brief Generation | `backend/main.py`, `backend/routers/`, `frontend/src/` |

---

## Detailed Contributions

### Member 1: Paper Discovery + Document Ingestion

**Files:**
- `backend/routers/discovery.py`
  - `POST /api/search` - Search arXiv and rank papers
  - `POST /api/ingest/{paper_id}` - Download PDF and extract sections
  - `GET /api/papers` - List all papers
  - `GET /api/papers/{paper_id}` - Get paper details

- `backend/database/paper_repo.py`
  - SQLite repository with `save()`, `get()`, `list_all()`
  - Papers and sections tables
  - Claim storage and retrieval

**Key Contributions:**
- Designed SQLite schema for papers, sections, claims
- Implemented TF-IDF ranking algorithm
- Integrated arXiv API for paper downloading
- Set up PyMuPDF for section extraction

---

### Member 2: Claim Extraction

**Files:**
- `backend/extraction/extractor.py`
  - `ClaimExtractor` class with LLM integration
  - `extract_from_section()` for single section
  - `extract_from_paper()` for all sections

- `backend/extraction/validator.py`
  - `ClaimValidator` with source sentence verification
  - 90% substring match threshold
  - `filter_valid()` for batch validation

- `backend/prompts/claim_extraction.py`
  - System prompt defining claim types
  - User prompt template with examples
  - `get_claim_extraction_prompt()` helper

**Key Contributions:**
- Designed claim schema with provenance tracking
- Implemented verbatim source validation
- Created prompt templates for LLM extraction
- Added retry logic for LLM failures

---

### Member 3: Cross-Source Synthesis

**Files:**
- `backend/synthesis/claim_grouper.py`
  - Keyword-based topic assignment
  - 6 predefined topic categories
  - `group_by_topic()` clustering

- `backend/synthesis/relation_detector.py`
  - `RelationDetector` with LLM comparison
  - `compare()` for claim pairs
  - `compare_group()` for topic groups

- `backend/synthesis/consensus_scorer.py`
  - Agreement ratio calculation
  - Conflict detection
  - Evidence strength classification

- `backend/synthesis/cross_source_pipeline.py`
  - `CrossSourcePipeline` orchestrator
  - End-to-end synthesis workflow

**Key Contributions:**
- Designed relation schema (agrees/contradicts/supports/gap)
- Implemented topic clustering algorithm
- Created consensus scoring system
- Built pipeline orchestration

---

### Member 4: FastAPI Backend + React Frontend + Brief Generation

**Backend Files:**
- `backend/main.py`
  - FastAPI app with CORS
  - Router mounting
  - Health check endpoint

- `backend/routers/claims.py`
  - `GET /api/papers/{paper_id}/claims`
  - `POST /api/papers/{paper_id}/extract`

- `backend/routers/synthesis.py`
  - `GET /api/synthesis`

- `backend/routers/brief.py`
  - `GET /api/brief`
  - `POST /api/brief/export`

- `backend/models/`
  - `paper.py`, `claim.py`, `relation.py`, `research_brief.py`
  - Complete Pydantic model definitions

- `backend/brief/generator.py`
  - `BriefGenerator` with LLM synthesis
  - `export_markdown()`, `export_bibtex()`

- `backend/brief/citation_formatter.py`
  - APA, BibTeX, inline citation formats

**Frontend Files:**
- `frontend/src/App.tsx`
  - React Router with 5 routes

- `frontend/src/api/client.ts`
  - Complete API client with TypeScript types
  - All endpoint functions

- `frontend/src/pages/Discovery.tsx`
  - Search interface with checkbox selection
  - Ingest functionality

- `frontend/src/pages/Papers.tsx`
  - Paper list with section expansion
  - Claim extraction trigger

- `frontend/src/pages/Claims.tsx`
  - Color-coded claim table
  - Type filtering
  - Detail modal

- `frontend/src/pages/Synthesis.tsx`
  - Topic cards with consensus scores
  - Conflict highlighting
  - Expandable details

- `frontend/src/pages/Brief.tsx`
  - Brief generation interface
  - MD/BibTeX export
  - Download functionality

- `frontend/src/App.css`
  - Complete styling for all components

**Key Contributions:**
- Built complete FastAPI application structure
- Created all 5 React pages with full functionality
- Implemented TypeScript type safety throughout
- Designed responsive CSS styling
- Added export functionality (MD, BibTeX, JSON)

---

## Documentation Contributions

**All Members:**
- `docs/architecture.md` - System design documentation
- `docs/demo_script.md` - Step-by-step walkthrough
- `docs/viva_qa.md` - Interview question answers

---

## Testing

| Module | Tests | Status |
|--------|-------|--------|
| Paper Discovery | 8 tests | ✅ Passing |
| Document Ingestion | 8 tests | ✅ Passing |
| Claim Extraction | 9 tests | ✅ Passing |
| Synthesis | 11 tests | ✅ Passing |
| Brief Generation | 13 tests | ✅ Passing |
| **Total** | **49 tests** | **✅ All Passing** |

---

## Key Technical Decisions

1. **SQLite over PostgreSQL** - Simpler for demo, easy upgrade path
2. **Keyword-based clustering** - Faster than sentence transformers
3. **Validation-first approach** - Reject hallucinations before synthesis
4. **Single-page React app** - Simple routing, fast navigation

---

## Time Distribution

| Activity | Estimated Time |
|----------|---------------|
| Backend setup + models | 2 hours |
| Paper discovery + ingestion | 3 hours |
| Claim extraction + validation | 3 hours |
| Cross-source synthesis | 4 hours |
| Brief generation | 2 hours |
| FastAPI routers + main | 2 hours |
| React frontend | 6 hours |
| Documentation | 2 hours |
| **Total** | **~24 hours** |

---

## Challenges Faced

1. **LLM rate limits** - Implemented exponential backoff
2. **PDF parsing variability** - Added graceful fallback
3. **Semantic Scholar API** - Awaiting key approval
4. **Claim validation threshold** - Tuned to 90% for balance

---

## Future Work

With more time, the team would add:
1. Sentence transformer embeddings for semantic clustering
2. Citation network visualization
3. Real-time WebSocket updates
4. Multi-user authentication
