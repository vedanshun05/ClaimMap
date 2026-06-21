"""
Brief Generator

Generate structured brief with traceable citations.
Support export to Markdown and PDF formats.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.config import config
from src.shared.utils import load_json, claims_from_dict, synthesis_from_dict, ingested_from_dict
from src.shared.models import SynthesisResult, Claim
from .template import BriefTemplate, CitationFormatter
from .exporter import MarkdownExporter, PDFExporter


class BriefGenerationAgent:
    """
    Agent responsible for generating the final research brief.

    Combines all previous agent outputs into a structured,
    traceable research brief with Markdown and PDF export.
    """

    def __init__(self):
        self.template = BriefTemplate()
        self.markdown_exporter = MarkdownExporter(self.template)
        self.pdf_exporter = PDFExporter(self.markdown_exporter)

    def generate_brief(
        self,
        topic: str,
        papers: list[dict] | None = None,
        claims: list[dict] | None = None,
        synthesis: dict | None = None,
    ) -> dict[str, Any]:
        """
        Generate a complete research brief.

        Args:
            topic: Research topic/question
            papers: List of paper dicts. If None, loads from data store.
            claims: List of claim dicts. If None, loads from data store.
            synthesis: Synthesis result dict. If None, loads from data store.

        Returns:
            Dictionary with brief data
        """
        if papers is None:
            filepath = config.data_dir / config.ingested_papers_file
            papers = load_json(filepath)

        if claims is None:
            filepath = config.data_dir / config.extracted_claims_file
            claims = claims_from_dict(load_json(filepath))

        if synthesis is None:
            filepath = config.data_dir / config.synthesis_file
            synthesis_dict = load_json(filepath)
            synthesis = synthesis_from_dict(synthesis_dict)

        print(f"[Agent 5] Generating brief for topic: '{topic}'")
        print(f"[Agent 5] Using {len(papers)} papers, {len(claims)} claims")

        brief_data = {
            "title": f"Research Brief: {topic}",
            "topic": topic,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "paper_count": len(papers),
            "papers": papers,
            "claims": claims,
            "themes": [t.to_dict() if hasattr(t, 'to_dict') else t for t in synthesis.themes],
            "areas_of_consensus": synthesis.areas_of_consensus,
            "areas_of_conflict": synthesis.areas_of_conflict,
            "evidence_gaps": synthesis.evidence_gaps,
            "executive_summary": self._generate_executive_summary(topic, synthesis, papers),
            "recommended_papers": self._get_recommended_papers(papers, synthesis),
        }

        return brief_data

    def _generate_executive_summary(
        self,
        topic: str,
        synthesis: SynthesisResult,
        papers: list,
    ) -> str:
        """Generate executive summary using LLM if available."""
        try:
            from ..claim_extractor.llm_client import LLMClient

            client = LLMClient()

            themes_summary = "\n".join([
                f"- {t.theme_name}: {t.summary}"
                for t in synthesis.themes[:5]
            ])

            prompt = f"""Based on the following research synthesis on "{topic}", write a 2-3 sentence executive summary.

Themes covered:
{themes_summary}

Papers analyzed: {len(papers)}

Write only the executive summary, no headers or formatting."""

            summary = client.generate(prompt, temperature=0.3)

            if summary:
                return summary

        except Exception:
            pass

        consensus_count = len(synthesis.areas_of_consensus)
        conflict_count = len(synthesis.areas_of_conflict)
        theme_count = len(synthesis.themes)

        return (
            f"This brief synthesizes findings from {len(papers)} papers on {topic}. "
            f"The analysis identified {theme_count} key themes, with {consensus_count} areas of consensus "
            f"and {conflict_count} areas of conflict or disagreement. "
            f"The evidence suggests ongoing research directions and open questions in this area."
        )

    def _get_recommended_papers(
        self,
        papers: list,
        synthesis,
    ) -> list[dict]:
        """Get recommended next papers based on synthesis."""
        recommendations = []

        theme_papers = {}
        for theme in synthesis.themes:
            for claim_id in theme.claim_ids:
                for paper in papers:
                    if claim_id.startswith(paper.get("paper_id", "")):
                        if theme.theme_id not in theme_papers:
                            theme_papers[theme.theme_id] = paper
                        break

        for theme_id, paper in theme_papers.items():
            if paper not in recommendations:
                recommendations.append(paper)

        recommendations.sort(key=lambda p: p.get("citation_count", 0), reverse=True)

        return recommendations[:5]

    def export_to_markdown(self, brief_data: dict, output_path: Path | None = None) -> Path:
        """Export brief to Markdown."""
        if output_path is None:
            output_path = config.output_dir / config.brief_md_file

        self.markdown_exporter.export(brief_data, output_path)
        return output_path

    def export_to_pdf(self, brief_data: dict, output_path: Path | None = None) -> Path | None:
        """Export brief to PDF."""
        if output_path is None:
            output_path = config.output_dir / config.brief_pdf_file

        try:
            self.pdf_exporter.export(brief_data, output_path)
            return output_path
        except Exception as e:
            print(f"[Agent 5] PDF export failed: {e}")
            return None

    def save_brief(self, brief_data: dict) -> tuple[Path, Path | None]:
        """Save brief in both Markdown and PDF formats."""
        md_path = self.export_to_markdown(brief_data)
        pdf_path = self.export_to_pdf(brief_data)

        return md_path, pdf_path


def main():
    """CLI entry point for Agent 5."""
    topic = "machine learning research"

    agent = BriefGenerationAgent()
    brief_data = agent.generate_brief(topic)
    md_path, pdf_path = agent.save_brief(brief_data)

    print(f"\n[Agent 5] Brief saved:")
    print(f"  Markdown: {md_path}")
    if pdf_path:
        print(f"  PDF: {pdf_path}")


if __name__ == "__main__":
    main()
