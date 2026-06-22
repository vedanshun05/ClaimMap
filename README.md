# AI Research Synthesis Engine

From 50 papers to one coherent research brief — in minutes, not weeks.

## Overview

A research synthesis platform that:
- Queries academic sources (arXiv, Semantic Scholar)
- Ingests and parses full-text PDFs
- Extracts claims with source traceability
- Synthesizes cross-source insights
- Generates structured research briefs with citations

## Architecture

Sequential pipeline via shared data store:

```
User Query → Paper Discovery → Document Processor → Claim Extractor
→ Synthesis Engine → Brief Generator → Markdown + PDF Output
```

## Quick Start

```bash
# Install dependencies
pip install -e .

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the pipeline
python -m src.paper_discovery --query "transformer attention mechanism"
```

## Project Structure

```
src/
├── paper_discovery/     # arXiv and Semantic Scholar API integration
├── document_processor/  # PDF parsing and structured extraction
├── claim_extractor/    # LLM-powered claim extraction
├── synthesis_engine/    # Thematic clustering and consensus analysis
├── brief_generator/    # Markdown and PDF export
└── shared/             # Config, models, and utilities
```

## API Keys

This project uses the **OpenAI SDK** with **OpenCode Zen** API (`deepseek-v4-flash-free`) as the primary LLM provider.

Get your API key:
- [OpenCode Zen](https://opencode.ai)

## Test Papers

For testing, use these well-known arXiv papers:

| Paper | arXiv ID | Direct PDF |
|-------|----------|-----------|
| Attention Is All You Need | 1706.03762 | https://arxiv.org/pdf/1706.03762 |
| BERT | 1810.04805 | https://arxiv.org/pdf/1810.04805 |
| GPT-3 | 2005.14165 | https://arxiv.org/pdf/2005.14165 |
| ResNet | 1512.03385 | https://arxiv.org/pdf/1512.03385 |
| CLIP | 2103.00020 | https://arxiv.org/pdf/2103.00020 |

## License

MIT
