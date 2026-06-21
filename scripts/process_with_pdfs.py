"""
Process only papers with local PDFs.

Usage:
    python scripts/process_with_pdfs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_processor.agent import DocumentIngestionAgent
from src.shared.config import config
from src.shared.utils import load_json, save_json, papers_from_dict


def main():
    # Load discovered papers
    filepath = config.data_dir / config.discovered_papers_file
    data = load_json(filepath)
    all_papers = papers_from_dict(data)

    print(f"Total discovered papers: {len(all_papers)}")

    # Get list of available PDFs
    pdf_dir = config.data_dir / "pdfs"
    available_pdfs = {p.stem.replace("arXiv:", "arXiv:") for p in pdf_dir.glob("*.pdf")}

    print(f"Available PDFs: {len(available_pdfs)}")
    for p in available_pdfs:
        print(f"  - {p}")

    # Filter to only papers with PDFs
    papers_with_pdfs = []
    for paper in all_papers:
        # Check both with and without version suffix
        paper_id = paper.paper_id
        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        for pdf_id in [paper_id, base_id, paper_id.replace("arXiv:", ""), base_id.replace("arXiv:", "")]:
            if f"arXiv:{pdf_id}" in available_pdfs or pdf_id in available_pdfs:
                papers_with_pdfs.append(paper)
                break

    print(f"\nPapers with local PDFs: {len(papers_with_pdfs)}")
    for p in papers_with_pdfs:
        print(f"  - {p.paper_id}: {p.title[:50]}...")

    # Process only papers with PDFs
    agent = DocumentIngestionAgent()
    ingested = []

    for paper in papers_with_pdfs:
        result = agent._ingest_single_paper(paper)
        if result:
            ingested.append(result)

    print(f"\nSuccessfully ingested: {len(ingested)} papers")

    # Save results
    if ingested:
        filepath = config.data_dir / config.ingested_papers_file
        data = [p.to_dict() for p in ingested]
        save_json(data, filepath)
        print(f"Saved to {filepath}")

        print("\n=== Ingested Papers Summary ===")
        for p in ingested:
            print(f"\n  {p.title[:60]}...")
            print(f"    Abstract: {len(p.abstract)} chars")
            print(f"    Methodology: {len(p.methodology)} chars")
            print(f"    Findings: {len(p.key_findings)} items")
            print(f"    Limitations: {len(p.limitations)} items")
            print(f"    Pages: {p.pages}")


if __name__ == "__main__":
    main()
