# Viva Q&A

## Data Flow Questions

### Q: How does data flow through the pipeline?

**A:** The pipeline follows a sequential architecture:

1. **Discovery** receives a user query, searches arXiv and Semantic Scholar APIs, ranks results by TF-IDF relevance, and returns paper metadata
2. **Document Ingestion** downloads selected paper PDFs, extracts text using PyMuPDF, splits into sections by heading, and stores in SQLite
3. **Claim Extraction** sends each section to LLM with prompt instructing extraction of claims with type (finding/hypothesis/limitation), source sentence, and page number
4. **Validation** checks that extracted `source_sentence` exists verbatim in original section text (90%+ substring match)
5. **Synthesis** groups claims by topic keywords, performs pairwise comparison via LLM to detect relations (agrees/contradicts/supports/gap), and calculates consensus scores
6. **Brief Generation** uses LLM to synthesize all data into structured brief with executive summary, themed sections, and recommendations

### Q: How do modules communicate?

**A:** Modules communicate through:
- **REST API** (FastAPI routers) for frontend-backend communication
- **SQLite database** for persistent storage between stages
- **Pydantic models** as the API contract ensuring type consistency

---

## Hallucination Prevention

### Q: How do you prevent LLM from hallucinating citations?

**A:** We implement strict source validation:

1. **verbatim requirement**: Every claim must include `source_sentence` - the exact text from the paper
2. **validation pass**: After LLM extraction, `ClaimValidator` checks if `source_sentence` exists in the original section text
3. **substring matching**: Uses 90% word overlap threshold for fuzzy matching
4. **rejection**: Claims failing validation are marked `is_validated=False` and excluded from synthesis

```python
# Validator checks:
if normalized_sentence in normalized_text:
    return True  # Valid
```

### Q: What if a claim is ambiguous?

**A:** The extraction prompt instructs: "If text is ambiguous, mark the claim type as 'hypothesis' rather than 'finding'"

---

## Conflict Detection

### Q: How do you detect conflicts between papers?

**A:** The `RelationDetector` compares claim pairs:

1. Sends both claims to LLM with comparison prompt
2. LLM returns relation type: `agrees`, `contradicts`, `supports`, or `gap`
3. Also returns explanation and confidence score
4. `ConsensusScorer` aggregates:
   - `has_conflict = any(contradicts)`
   - `agreement_ratio = agrees / total`
   - `evidence_strength = strong/moderate/thin`

---

## Finding vs Hypothesis vs Limitation

### Q: How do you distinguish between findings, hypotheses, and limitations?

**A:** The LLM prompt defines clear criteria:

- **finding**: Proven results with evidence ("Our model achieves 95% accuracy...")
- **hypothesis**: Proposed but unproven claims ("We hypothesize that...") - also used when text is ambiguous
- **limitation**: Acknowledged weaknesses ("One limitation is..." or "This approach cannot handle...")

The validator does not check type correctness - this is delegated to LLM judgment with low temperature (0.1) for consistency.

---

## Tech Stack Questions

### Q: Why FastAPI?

**A:**
- Automatic OpenAPI/Swagger documentation
- Pydantic integration for data validation
- Async support for concurrent requests
- Easy CORS setup for frontend-backend
- Simple route organization with routers

### Q: Why React + TypeScript?

**A:**
- Component-based architecture matches our page structure
- TypeScript catches errors at compile time
- Vite provides fast HMR for development
- Strong ecosystem for routing, HTTP clients

### Q: Why litellm?

**A:**
- Unified interface for multiple LLM providers
- Easy fallback between NVIDIA NIM and Gemini
- Standard OpenAI-compatible API
- No need to rewrite code when switching models

### Q: Why SQLite over other databases?

**A:**
- Zero configuration - file-based
- Sufficient for single-user demo scale
- Can be swapped for PostgreSQL in production
- No separate server process needed

---

## Error Handling

### Q: What happens if PDF parsing fails?

**A:**
- `PDFParser` wraps PyMuPDF in try-except
- On failure, marks section as "unparseable"
- Extracts raw text without section splits
- Pipeline continues with partial data

### Q: What if no results are found?

**A:**
- Returns empty array with `total: 0`
- Frontend shows "No papers found" message
- User can try different query

### Q: How do you handle API rate limits?

**A:**
- arXiv: 1 req/3 sec - implemented with delay
- Gemini: 60 req/min - litellm handles automatically
- Exponential backoff on 429 responses
- In-memory cache for repeated queries

---

## Future Improvements

### Q: What would you add with more time?

**A:**
1. **Sentence transformers** for semantic clustering instead of keyword matching
2. **Citation network analysis** using Semantic Scholar's citation graph
3. **PDF upload** for user-provided papers (currently only arXiv IDs)
4. **Real-time updates** using WebSockets for long extractions
5. **User authentication** for multi-user support
6. **PostgreSQL** upgrade for production scale

---

## Team Split Rationale

### Q: How was work divided?

**A:** Based on the spec's module assignments:

- **Module A**: Paper Discovery + Document Ingestion (foundational)
- **Module B**: Claim Extraction (core innovation)
- **Module C**: Cross-Source Synthesis (AI/ML heavy)
- **Module D**: FastAPI Backend + React Frontend + Brief Generation (full-stack)

Work was parallelized by creating backend structure first, then frontend.
