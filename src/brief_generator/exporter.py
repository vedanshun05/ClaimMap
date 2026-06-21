"""Markdown and PDF export utilities."""

from pathlib import Path
from datetime import datetime


class MarkdownExporter:
    """Export research brief to Markdown."""

    def __init__(self, template):
        self.template = template

    def export(
        self,
        brief_data: dict,
        output_path: Path,
    ) -> None:
        """
        Export brief to Markdown file.

        Args:
            brief_data: Dictionary containing brief components
            output_path: Path to save the Markdown file
        """
        markdown_content = self._generate_markdown(brief_data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"[MarkdownExporter] Saved to {output_path}")

    def _generate_markdown(self, data: dict) -> str:
        """Generate Markdown content from brief data."""
        template_str = self.template.get_markdown_template()

        template_str = template_str.format(
            title=data.get("title", "Research Brief"),
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            topic=data.get("topic", "Research Topic"),
            paper_count=data.get("paper_count", 0),
            executive_summary=data.get("executive_summary", "No summary available."),
            key_findings=self._format_findings(data.get("themes", [])),
            areas_of_consensus=self._format_list(data.get("areas_of_consensus", [])),
            areas_of_conflict=self._format_list(data.get("areas_of_conflict", [])),
            evidence_gaps=self._format_list(data.get("evidence_gaps", [])),
            recommended_papers=self._format_papers(data.get("recommended_papers", [])),
            references=self._format_references(data.get("papers", [])),
        )

        return template_str

    def _format_findings(self, themes: list) -> str:
        """Format key findings section."""
        if not themes:
            return "No findings available."

        lines = []
        for theme in themes[:10]:
            lines.append(self.template.format_theme_section(theme))
            lines.append("")

        return "\n".join(lines)

    def _format_list(self, items: list) -> str:
        """Format a list of items."""
        if not items:
            return "None identified."

        return "\n".join(f"- {item}" for item in items)

    def _format_papers(self, papers: list) -> str:
        """Format recommended papers."""
        if not papers:
            return "No recommendations available."

        lines = []
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get("title", "Unknown")[:60]
            url = paper.get("url", "")
            lines.append(f"{i}. [{title}...]({url})")

        return "\n".join(lines)

    def _format_references(self, papers: list) -> str:
        """Format references section."""
        if not papers:
            return "No references available."

        lines = []
        for paper in papers:
            citation = self.template.format_apa(paper)
            lines.append(f"- {citation}")

        return "\n".join(lines)


class PDFExporter:
    """Export research brief to PDF."""

    def __init__(self, markdown_exporter: MarkdownExporter):
        self.markdown_exporter = markdown_exporter

    def export(
        self,
        brief_data: dict,
        output_path: Path,
        markdown_path: Path | None = None,
    ) -> None:
        """
        Export brief to PDF file.

        Args:
            brief_data: Dictionary containing brief components
            output_path: Path to save the PDF file
            markdown_path: Optional path to intermediate Markdown file
        """
        if markdown_path is None:
            markdown_path = output_path.with_suffix(".md")

        self.markdown_exporter.export(brief_data, markdown_path)

        try:
            import markdown

            html_content = markdown.markdown(
                markdown_path.read_text(encoding="utf-8"),
                extensions=["tables", "fenced_code"],
            )

            html_full = self._wrap_in_html(html_content)

            self._convert_to_pdf(html_full, output_path)

            print(f"[PDFExporter] Saved to {output_path}")

        except ImportError:
            print("[PDFExporter] markdown library not installed, PDF export skipped")
            print(f"[PDFExporter] Markdown file available at: {markdown_path}")
        except Exception as e:
            print(f"[PDFExporter] Error converting to PDF: {e}")
            print(f"[PDFExporter] Markdown file available at: {markdown_path}")

    def _wrap_in_html(self, content: str) -> str:
        """Wrap Markdown content in HTML template."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; }}
        code {{ background: #f4f4f4; padding: 2px 6px; }}
        pre {{ background: #f4f4f4; padding: 15px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ccc; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    def _convert_to_pdf(self, html_content: str, output_path: Path) -> None:
        """Convert HTML to PDF."""
        try:
            from weasyprint import HTML

            HTML(string=html_content).write_pdf(str(output_path))
        except ImportError:
            raise ImportError("weasyprint not installed")
