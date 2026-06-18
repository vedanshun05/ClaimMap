"""Discovery router - handles paper search, ingestion, and upload."""

import sys
import os
import re
import hashlib
import json
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from models.paper import Paper, PaperSearchResult, SearchRequest, SearchResponse, Section
from database import paper_repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["discovery"])

PAPERS_DIR = Path("papers")
PAPERS_DIR.mkdir(exist_ok=True)


def _strip_arxiv_version(paper_id: str) -> str:
    """Strip arXiv version suffix (e.g., '1809.04281v3' -> '1809.04281')."""
    return re.sub(r'v\d+$', '', paper_id)


def _score_relevance(title: str, abstract: str, query: str) -> float:
    tokens = re.findall(r'\w+', query.lower())
    title_l = title.lower()
    abstract_l = abstract.lower()
    score = 0.0
    for tok in tokens:
        score += 2.0 * title_l.count(tok)
        score += 1.0 * abstract_l.count(tok)
    return round(score, 2)


def _search_arxiv_native(query: str, max_results: int = 10) -> list[dict]:
    import requests
    import xml.etree.ElementTree as ET

    url = (
        f"https://export.arxiv.org/api/query"
        f"?search_query=all:{requests.utils.quote(query)}"
        f"&start=0&max_results={max_results}"
        f"&sortBy=relevance&sortOrder=descending"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"arXiv native search failed: {e}")
        return []

    root = ET.fromstring(resp.content)
    ns = "{http://www.w3.org/2005/Atom}"
    papers = []

    for entry in root.findall(f"{ns}entry"):
        title_el = entry.find(f"{ns}title")
        summary_el = entry.find(f"{ns}summary")
        if title_el is None or summary_el is None:
            continue

        title = re.sub(r'\s+', ' ', title_el.text or "").strip()
        summary = re.sub(r'\s+', ' ', summary_el.text or "").strip()

        authors = [
            (a.find(f"{ns}name").text or "").strip()
            for a in entry.findall(f"{ns}author")
            if a.find(f"{ns}name") is not None and a.find(f"{ns}name").text
        ]

        published = ""
        pub_el = entry.find(f"{ns}published")
        if pub_el is not None and pub_el.text:
            published = pub_el.text[:10]

        pdf_link = None
        for link in entry.findall(f"{ns}link"):
            href = link.attrib.get("href", "")
            if "pdf" in href:
                pdf_link = href
                break
            if "/abs/" in href and pdf_link is None:
                pdf_link = href.replace("/abs/", "/pdf/")

        entry_id = entry.find(f"{ns}id")
        raw_id = entry_id.text.split("/")[-1] if entry_id is not None and entry_id.text else ""
        arxiv_id = _strip_arxiv_version(raw_id)

        score = _score_relevance(title, summary, query)
        if score == 0:
            score = 0.1

        papers.append({
            "paper_id": f"arXiv:{arxiv_id}",
            "title": title,
            "authors": authors,
            "year": int(published[:4]) if published and published[:4].isdigit() else 0,
            "abstract": summary,
            "url": pdf_link or "",
            "source": "arxiv",
            "relevance_score": score,
            "citation_count": 0,
        })

    papers.sort(key=lambda p: p["relevance_score"], reverse=True)
    return papers


def _search_arxiv_lib(query: str, max_results: int = 10) -> list[dict]:
    try:
        from src.paper_discovery import ArxivClient
        arxiv_client = ArxivClient()
        results = arxiv_client.search(query=query, max_results=max_results)
        papers = []
        for r in results:
            year = int(r.published_date[:4]) if r.published_date and r.published_date[:4].isdigit() else 0

            raw_id = r.paper_id.replace("arXiv:", "") if r.paper_id.startswith("arXiv:") else r.paper_id
            clean_id = _strip_arxiv_version(raw_id)

            score = _score_relevance(r.title, r.abstract, query)
            if score == 0:
                score = 0.1
            papers.append({
                "paper_id": f"arXiv:{clean_id}",
                "title": r.title,
                "authors": r.authors,
                "year": year,
                "abstract": r.abstract,
                "url": r.url,
                "source": "arxiv",
                "relevance_score": score,
                "citation_count": 0,
            })
        return papers
    except Exception as e:
        logger.warning(f"arXiv lib search failed: {e}")
        return []


def rank_papers(query: str, papers: list[dict]) -> list[dict]:
    scored = []
    query_words = set(query.lower().split())
    for paper in papers:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        paper_words = set(text.split())
        overlap = len(query_words & paper_words)
        paper["relevance_score"] = round(overlap / len(query_words), 3) if overlap > 0 else paper.get("relevance_score", 0.0)
        if paper["relevance_score"] == 0:
            continue
        scored.append(paper)
    scored.sort(key=lambda p: p["relevance_score"], reverse=True)
    return scored


@router.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest) -> SearchResponse:
    all_papers = []

    papers = await asyncio.to_thread(_search_arxiv_lib, request.query, request.max_results)
    if not papers:
        logger.info("arXiv lib search returned empty, trying native API")
        papers = await asyncio.to_thread(_search_arxiv_native, request.query, request.max_results)

    all_papers.extend(papers)

    seen = set()
    unique = []
    for p in all_papers:
        pid = p.get("paper_id", "")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)

    ranked = rank_papers(request.query, unique)

    return SearchResponse(
        papers=[PaperSearchResult(**p) for p in ranked[:request.max_results]],
        total=min(len(ranked), request.max_results),
    )


@router.post("/ingest/{paper_id:path}")
async def ingest_paper(paper_id: str) -> dict:
    try:
        result = await asyncio.to_thread(_ingest_paper_sync, paper_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest paper {paper_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest paper: {str(e)}")


def _ingest_paper_sync(paper_id: str) -> dict:
    """Synchronous paper ingestion — runs in thread pool."""
    import arxiv
    import requests as http_requests

    client = arxiv.Client()

    raw_id = paper_id
    if raw_id.startswith("arXiv:"):
        raw_id = raw_id.replace("arXiv:", "", 1)
    arxiv_id = _strip_arxiv_version(raw_id)

    logger.info(f"Ingesting arXiv paper: raw={paper_id}, clean={arxiv_id}")

    search = arxiv.Search(id_list=[arxiv_id])
    result = next(client.results(search))

    result_id = result.entry_id.split("/")[-1]
    result_id_clean = _strip_arxiv_version(result_id)

    paper = Paper(
        id=f"arXiv:{result_id_clean}",
        title=result.title,
        authors=[a.name for a in result.authors],
        year=result.published.year,
        abstract=result.summary,
        source="arxiv",
        source_id=result.entry_id,
        pdf_path=None,
    )

    download_path = PAPERS_DIR / f"{paper.id.replace(':', '_')}.pdf"
    download_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_url = result.pdf_url
    if pdf_url:
        resp = http_requests.get(pdf_url, timeout=60)
        resp.raise_for_status()
        with open(str(download_path), "wb") as f:
            f.write(resp.content)
        paper.pdf_path = str(download_path)
    else:
        raise HTTPException(status_code=500, detail=f"No PDF URL found for paper {arxiv_id}")

    sections = []
    try:
        import fitz
        doc = fitz.open(str(download_path))
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                sections.append(Section(
                    paper_id=paper.id,
                    heading=f"Page {page_num + 1}",
                    content=text,
                    page_number=page_num + 1,
                ))
        doc.close()
    except Exception as e:
        logger.warning(f"PDF parsing error: {e}")

    paper.sections = sections
    paper_repo.save(paper)

    return {
        "success": True,
        "paper_id": paper.id,
        "title": paper.title,
        "sections_count": len(sections),
    }


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    safe_name = re.sub(r'[^\w\-.]', '_', file.filename)
    save_path = PAPERS_DIR / safe_name

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    result = await asyncio.to_thread(_parse_and_save_upload, safe_name, save_path)
    return result


def _parse_and_save_upload(safe_name: str, save_path: Path) -> dict:
    """Parse uploaded PDF and save — runs in thread pool."""
    sections = []
    paper_id = safe_name.replace(".pdf", "")

    try:
        import fitz
        doc = fitz.open(str(save_path))
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip() and len(text.strip()) > 50:
                sections.append(Section(
                    paper_id=f"upload:{paper_id}",
                    heading=f"Page {page_num + 1}",
                    content=text,
                    page_number=page_num + 1,
                ))
        doc.close()
    except Exception as e:
        logger.warning(f"PDF parsing error for uploaded file: {e}")

    abstract = sections[0].content[:500] if sections else ""
    title = safe_name.replace("_", " ").replace(".pdf", "")

    paper = Paper(
        id=f"upload:{paper_id}",
        title=title,
        authors=["Unknown (uploaded)"],
        year=0,
        abstract=abstract,
        source="upload",
        source_id=safe_name,
        pdf_path=str(save_path),
        sections=sections,
    )

    paper_repo.save(paper)

    return {
        "success": True,
        "paper_id": paper.id,
        "title": paper.title,
        "sections_count": len(sections),
        "filename": safe_name,
    }


@router.get("/papers", response_model=list[Paper])
async def list_papers() -> list[Paper]:
    return paper_repo.list_all()


@router.get("/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str) -> Paper:
    paper = paper_repo.get(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper