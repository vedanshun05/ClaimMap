# Demo Script

## Pre-Demo Checklist
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 5173
- [ ] API keys configured in `.env`
- [ ] Sample papers available

## Step-by-Step Walkthrough

### Step 1: Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify: Open http://localhost:8000/docs to see Swagger UI

### Step 2: Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

Verify: Open http://localhost:5173 to see the React app

### Step 3: Paper Discovery (5 minutes)

1. Navigate to **Discovery** page
2. Enter query: "transformer attention mechanism"
3. Click **Search**
4. View ranked results with relevance scores
5. Select 2-3 papers using checkboxes
6. Click **Ingest Selected**
7. Wait for successful ingestion message

**What happens:**
- arXiv API is queried
- Papers are ranked by TF-IDF word overlap
- Selected papers are downloaded as PDFs
- PDF sections are extracted using PyMuPDF
- Papers stored in SQLite database

### Step 4: View Papers (2 minutes)

1. Navigate to **Papers** page
2. See list of ingested papers
3. Click on a paper to expand
4. View extracted sections with page numbers
5. Click **Extract Claims** button

**What happens:**
- Paper details loaded from SQLite
- All sections sent to LLM for claim extraction
- Claims are validated against source text
- Valid claims saved to database

### Step 5: Review Claims (3 minutes)

1. Navigate to **Claims** page
2. View stats bar showing claim type distribution
3. Filter by claim type using buttons
4. Click on a claim to see details:
   - Full claim text
   - Source sentence (verbatim from paper)
   - Section and page number
   - Validation status

**What happens:**
- All claims loaded from database
- Color-coded by type:
  - 🟢 Green = Finding (proven result)
  - 🟡 Yellow = Hypothesis (proposed)
  - 🔴 Red = Limitation (acknowledged weakness)

### Step 6: Synthesis (3 minutes)

1. Navigate to **Synthesis** page
2. View overall stats (papers, claims, topics)
3. See areas of consensus
4. See areas of conflict (if any)
5. See evidence gaps
6. Click on a topic card to expand:
   - View all claims in topic
   - See relations between claims
   - See consensus strength

**What happens:**
- Claims grouped by topic using keyword matching
- Claim pairs compared using LLM
- Relations classified: agrees, contradicts, supports, gap
- Consensus score calculated per topic

### Step 7: Generate Brief (3 minutes)

1. Navigate to **Brief** page
2. Enter research query/topic
3. Click **Regenerate**
4. View generated brief:
   - Executive summary
   - Themed sections
   - Consensus/conflict areas
   - Open questions
5. Export as Markdown or BibTeX

**What happens:**
- LLM generates structured brief from synthesis
- Citation badges created for references
- Brief exported in requested format

### Step 8: Full Flow Demo (2 minutes)

Show the complete flow end-to-end:
1. Discovery → Search & ingest new paper
2. Papers → Extract claims
3. Claims → Verify claim types
4. Synthesis → See new topics formed
5. Brief → Regenerate with new paper included

## Demo Commands

### Start Backend
```bash
cd /path/to/project/backend
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd /path/to/project/frontend
npm run dev
```

### Run Tests
```bash
cd /path/to/project
pytest tests/ -v
```

## Test Queries

For demo, use these well-known papers:
- "Attention Is All You Need" (arXiv:1706.03762)
- "BERT: Pre-training of Deep Bidirectional Transformers" (arXiv:1810.04805)

Example queries:
- "transformer attention mechanism"
- "BERT language model pre-training"
- "neural machine translation"
- "deep bidirectional transformers"
