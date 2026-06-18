"""SQLite paper repository for FastAPI backend."""

import sys
from pathlib import Path
import json
import sqlite3
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from models.paper import Paper, Section


class PaperRepository:
    """SQLite repository for papers and sections."""

    def __init__(self, db_path: str = "backend/database/papers.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                abstract TEXT,
                source TEXT NOT NULL,
                source_id TEXT,
                pdf_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                heading TEXT,
                content TEXT,
                page_number INTEGER,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                text TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                source_section TEXT,
                source_sentence TEXT,
                page_number INTEGER,
                confidence REAL DEFAULT 0.8,
                is_validated INTEGER DEFAULT 0,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthesis_cache (
                claims_hash TEXT PRIMARY KEY,
                result TEXT NOT NULL,
                claim_count INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brief_cache (
                cache_key TEXT PRIMARY KEY,
                result TEXT NOT NULL,
                claim_count INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def save(self, paper: Paper) -> Paper:
        """Save a paper to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        authors_json = json.dumps(paper.authors)

        cursor.execute("""
            INSERT OR REPLACE INTO papers (id, title, authors, year, abstract, source, source_id, pdf_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper.id,
            paper.title,
            authors_json,
            paper.year,
            paper.abstract,
            paper.source,
            paper.source_id,
            paper.pdf_path,
            paper.created_at or datetime.now()
        ))

        cursor.execute("DELETE FROM sections WHERE paper_id = ?", (paper.id,))

        for section in paper.sections:
            cursor.execute("""
                INSERT INTO sections (paper_id, heading, content, page_number)
                VALUES (?, ?, ?, ?)
            """, (paper.id, section.heading, section.content, section.page_number))

        conn.commit()
        conn.close()
        return paper

    def get(self, paper_id: str) -> Optional[Paper]:
        """Get a paper by ID with its sections."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        cursor.execute("SELECT * FROM sections WHERE paper_id = ? ORDER BY page_number", (paper_id,))
        section_rows = cursor.fetchall()

        authors = json.loads(row["authors"] or "[]")

        sections = [
            Section(
                id=sr["id"],
                paper_id=sr["paper_id"],
                heading=sr["heading"] or "",
                content=sr["content"] or "",
                page_number=sr["page_number"] or 0
            )
            for sr in section_rows
        ]

        paper = Paper(
            id=row["id"],
            title=row["title"],
            authors=authors,
            year=row["year"] or 0,
            abstract=row["abstract"] or "",
            source=row["source"],
            source_id=row["source_id"] or "",
            pdf_path=row["pdf_path"],
            sections=sections,
            created_at=row["created_at"]
        )

        conn.close()
        return paper

    def list_all(self) -> list[Paper]:
        """List all papers."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM papers ORDER BY created_at DESC")
        rows = cursor.fetchall()

        papers = []
        for row in rows:
            paper = self.get(row["id"])
            if paper:
                papers.append(paper)

        conn.close()
        return papers

    def delete(self, paper_id: str) -> bool:
        """Delete a paper and its sections."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sections WHERE paper_id = ?", (paper_id,))
        cursor.execute("DELETE FROM claims WHERE paper_id = ?", (paper_id,))
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def save_claim(self, paper_id: str, claim: dict) -> dict:
        """Save a claim for a paper."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO claims (paper_id, text, claim_type, source_section, source_sentence, page_number, confidence, is_validated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            claim["text"],
            claim["claim_type"],
            claim.get("source_section", ""),
            claim.get("source_sentence", ""),
            claim.get("page_number", 0),
            claim.get("confidence", 0.8),
            1 if claim.get("is_validated", False) else 0
        ))

        claim_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"id": claim_id, "paper_id": paper_id, **claim}

    def get_claims(self, paper_id: str) -> list[dict]:
        """Get all claims for a paper."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM claims WHERE paper_id = ?", (paper_id,))
        rows = cursor.fetchall()

        claims = []
        for row in rows:
            claims.append({
                "id": row["id"],
                "paper_id": row["paper_id"],
                "text": row["text"],
                "claim_type": row["claim_type"],
                "source_section": row["source_section"],
                "source_sentence": row["source_sentence"],
                "page_number": row["page_number"],
                "confidence": row["confidence"],
                "is_validated": bool(row["is_validated"])
            })

        conn.close()
        return claims

    def get_all_claims(self) -> list[dict]:
        """Get all claims from all papers."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM claims ORDER BY paper_id, id")
        rows = cursor.fetchall()

        claims = []
        for row in rows:
            claims.append({
                "id": row["id"],
                "paper_id": row["paper_id"],
                "text": row["text"],
                "claim_type": row["claim_type"],
                "source_section": row["source_section"],
                "source_sentence": row["source_sentence"],
                "page_number": row["page_number"],
                "confidence": row["confidence"],
                "is_validated": bool(row["is_validated"])
            })

        conn.close()
        return claims

    def clear_claims(self, paper_id: str) -> None:
        """Clear all claims for a paper."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM claims WHERE paper_id = ?", (paper_id,))
        conn.commit()
        conn.close()

    def get_synthesis_cache(self, claims_hash: str) -> Optional[dict]:
        """Get cached synthesis result."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT result, timestamp FROM synthesis_cache WHERE claims_hash = ?", (claims_hash,))
        row = cursor.fetchone()
        conn.close()
        if row:
            import time
            # 24-hour TTL (86400 seconds)
            if time.time() - row["timestamp"] < 86400:
                return json.loads(row["result"])
        return None

    def save_synthesis_cache(self, claims_hash: str, result: dict, claim_count: int) -> None:
        """Save synthesis result to cache."""
        import time
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO synthesis_cache (claims_hash, result, claim_count, timestamp)
            VALUES (?, ?, ?, ?)
        """, (claims_hash, json.dumps(result), claim_count, time.time()))
        conn.commit()
        conn.close()

    def get_brief_cache(self, cache_key: str) -> Optional[dict]:
        """Get cached brief result."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT result, timestamp FROM brief_cache WHERE cache_key = ?", (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            import time
            # 24-hour TTL
            if time.time() - row["timestamp"] < 86400:
                return json.loads(row["result"])
        return None

    def save_brief_cache(self, cache_key: str, result: dict, claim_count: int) -> None:
        """Save brief result to cache."""
        import time
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO brief_cache (cache_key, result, claim_count, timestamp)
            VALUES (?, ?, ?, ?)
        """, (cache_key, json.dumps(result), claim_count, time.time()))
        conn.commit()
        conn.close()


paper_repo = PaperRepository()
