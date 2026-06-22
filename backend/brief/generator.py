"""Research brief generator with robust JSON parsing and async LLM calls."""

import sys
from pathlib import Path
import json
import re
import asyncio
import logging
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from prompts import get_brief_generation_prompt
from citation_formatter import formatter

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RATE_LIMIT_DELAY = 0.5

_ENV_LOADED = False


def _load_env_once():
    """Load environment variables from .env file, ensuring it only runs once."""
    global _ENV_LOADED
    if not _ENV_LOADED:
        from dotenv import load_dotenv
        import os
        load_dotenv(Path(__file__).parent.parent.parent / ".env", override=False)
        load_dotenv(Path(__file__).parent.parent / ".env", override=False)
        _ENV_LOADED = True


def _extract_json_from_text(text: str) -> Optional[dict]:
    """Extract a JSON object from a raw text string, handling code blocks."""
    text = text.strip()

    cleaned = re.sub(r'```(?:json)?\s*', '', text)
    cleaned = cleaned.replace('```', '').strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass

    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(cleaned[start:end + 1])
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError):
            pass

    return None


async def _call_llm_async(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Async LLM call for brief generation."""
    from llm_fallback import llm_completion

    for attempt in range(MAX_RETRIES):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            return await llm_completion(messages=messages, temperature=0.3)

        except Exception as e:
            logger.warning(f"[BriefGenerator] LLM attempt {attempt + 1} failed: {e}")
            if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                wait_time = 5 * (attempt + 1)
                logger.info(f"Rate limited, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1.5 ** attempt)
                continue
            logger.error("[BriefGenerator] All LLM attempts failed")
            return None
    return None


class BriefGenerator:
    """Generates structured research briefs from synthesis data."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def generate_async(
        self,
        query: str,
        papers: list[dict],
        claims: list[dict],
        synthesis: dict
    ) -> dict:
        """Generate a research brief with mandatory citations (async)."""
        themes_json = self._format_themes(synthesis.get("topics", []))
        consensus = "\n".join(f"- {c}" for c in synthesis.get("areas_of_consensus", []))
        conflicts = "\n".join(f"- {c}" for c in synthesis.get("areas_of_conflict", []))
        gaps = "\n".join(f"- {g}" for g in synthesis.get("evidence_gaps", []))

        if not consensus:
            consensus = "None identified"
        if not conflicts:
            conflicts = "None identified"
        if not gaps:
            gaps = "None identified"

        system_prompt, user_prompt = get_brief_generation_prompt(
            query=query,
            paper_count=len(papers),
            themes_json=themes_json,
            consensus=consensus,
            conflicts=conflicts,
            gaps=gaps
        )

        raw = await _call_llm_async(system_prompt, user_prompt)

        if raw:
            parsed = _extract_json_from_text(raw)
            if parsed and isinstance(parsed, dict):
                parsed["papers_analyzed"] = len(papers)
                parsed["query"] = query
                return parsed

        return self._generate_fallback(query, papers, synthesis)

    def generate(self, query: str, papers: list[dict], claims: list[dict], synthesis: dict) -> dict:
        """Synchronous wrapper for generate_async."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.generate_async(query, papers, claims, synthesis))
                    return future.result(timeout=300)
        except RuntimeError:
            pass
        return asyncio.run(self.generate_async(query, papers, claims, synthesis))

    def _format_themes(self, topics: list[dict]) -> str:
        if not topics:
            return "No themes identified"

        lines = []
        for topic in topics:
            topic_name = topic.get("topic", "Unknown")
            claims = topic.get("claims", [])
            consensus = topic.get("consensus", {})

            lines.append(f"\n## {topic_name}")
            lines.append(f"Evidence strength: {consensus.get('evidence_strength', 'unknown')}")
            lines.append(f"Claims ({len(claims)}):")
            for claim in claims[:5]:
                paper_title = claim.get("paper_id", "Unknown")
                page = claim.get("page_number", "?")
                text = claim.get("text", "")[:150]
                lines.append(f"  - [{paper_title}, p.{page}] {text}")

        return "\n".join(lines)

    def _generate_fallback(self, query: str, papers: list[dict], synthesis: dict) -> dict:
        themes = []
        for t in synthesis.get("topics", []):
            theme_claims = t.get("claims", [])
            evidence_count = len(set(c.get("paper_id") for c in theme_claims))
            themes.append({
                "theme": t.get("topic", "Unknown"),
                "summary": f"{len(theme_claims)} claims identified across {evidence_count} paper(s)",
                "supporting_claim_ids": [str(c.get("id", "")) for c in theme_claims[:5]],
                "consensus_level": t.get("consensus", {}).get("evidence_strength", "thin"),
                "evidence_count": evidence_count,
            })

        evidence_index = []
        for t in synthesis.get("topics", []):
            theme_claims = t.get("claims", [])
            n_papers = len(set(c.get("paper_id") for c in theme_claims))
            strength = "strong" if n_papers >= 3 else "moderate" if n_papers >= 2 else "thin"
            evidence_index.append({
                "finding": t.get("topic", "Unknown"),
                "strength": strength,
                "supporting_papers": n_papers,
            })

        return {
            "query": query,
            "papers_analyzed": len(papers),
            "executive_summary": f"Research brief on '{query}' analyzing {len(papers)} papers with {synthesis.get('total_claims', 0)} claims.",
            "themes": themes,
            "areas_of_consensus": synthesis.get("areas_of_consensus", []),
            "areas_of_conflict": synthesis.get("areas_of_conflict", []),
            "evidence_strength_index": evidence_index,
            "open_questions": synthesis.get("evidence_gaps", []),
            "recommended_next_papers": []
        }

    def export_markdown(self, brief: dict, papers: list[dict]) -> str:
        lines = [
            f"# Research Brief: {brief.get('query', 'Research')}",
            "",
            f"**Generated**: {self._timestamp()}",
            f"**Papers Analyzed**: {brief.get('papers_analyzed', 0)}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            brief.get("executive_summary", "No summary available."),
            "",
            "---",
            "",
            "## Key Themes",
            ""
        ]

        for theme in brief.get("themes", []):
            lines.append(f"### {theme.get('theme', 'Unknown Theme')}")
            lines.append(f"**Evidence**: {theme.get('consensus_level', 'unknown')} ({theme.get('evidence_count', '?')} papers)")
            lines.append("")
            lines.append(theme.get("summary", "No summary available."))
            lines.append("")

        if brief.get("evidence_strength_index"):
            lines.extend(["---", "", "## Evidence Strength Index", ""])
            lines.append("| Finding | Strength | Papers |")
            lines.append("|---------|----------|--------|")
            for entry in brief["evidence_strength_index"]:
                icon = {"strong": "🟢", "moderate": "🟡", "thin": "⚪"}.get(entry.get("strength", "thin"), "⚪")
                lines.append(f"| {icon} {entry.get('finding', '')} | {entry.get('strength', '')} | {entry.get('supporting_papers', 0)} |")
            lines.append("")

        if brief.get("areas_of_consensus"):
            lines.extend(["---", "", "## Areas of Consensus", ""])
            for item in brief["areas_of_consensus"]:
                lines.append(f"- {item}")
            lines.append("")

        if brief.get("areas_of_conflict"):
            lines.extend(["---", "", "## Areas of Conflict", ""])
            for item in brief["areas_of_conflict"]:
                lines.append(f"- {item}")
            lines.append("")

        if brief.get("open_questions"):
            lines.extend(["---", "", "## Open Questions", ""])
            for item in brief["open_questions"]:
                lines.append(f"- {item}")
            lines.append("")

        lines.extend(["---", "", "## References", ""])
        for paper in papers:
            lines.append(formatter.format_markdown(paper))

        return "\n".join(lines)

    def export_bibtex(self, papers: list[dict]) -> str:
        return "\n\n".join(formatter.format_bibtex(p) for p in papers)

    def _timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")


generator = BriefGenerator()