"""Citation formatter for research briefs."""

from typing import Optional


class CitationFormatter:
    """Formats citations in various styles."""

    @staticmethod
    def format_inline(claim: dict, paper: dict) -> str:
        """
        Format an inline citation for a claim.

        Args:
            claim: Claim dictionary
            paper: Paper dictionary

        Returns:
            Formatted inline citation like "[Paper Title, §Section]"
        """
        title = paper.get("title", "Unknown")[:40]
        section = claim.get("source_section", "")

        return f"[{title}..., §{section}]"

    @staticmethod
    def format_bibtex(paper: dict) -> str:
        """
        Format a paper as BibTeX entry.

        Args:
            paper: Paper dictionary

        Returns:
            BibTeX formatted string
        """
        paper_id = paper.get("id", "unknown").replace(":", "_").replace("/", "_")
        title = paper.get("title", "Unknown Title")
        authors = paper.get("authors", [])
        year = paper.get("year", 2024)

        author_str = " and ".join(authors[:3])
        if len(authors) > 3:
            author_str += " et al."

        lines = [
            f"@article{{{paper_id},",
            f"  title = {{{title}}},",
            f"  author = {{{author_str}}},",
            f"  year = {{{year}}},",
            f"  url = {{{paper.get('url', '')}}},",
            "}"
        ]

        return "\n".join(lines)

    @staticmethod
    def format_apa(paper: dict) -> str:
        """
        Format a paper as APA citation.

        Args:
            paper: Paper dictionary

        Returns:
            APA formatted citation
        """
        authors = paper.get("authors", [])
        year = paper.get("year", 2024)
        title = paper.get("title", "Unknown Title")

        if authors:
            first_names = [a.split()[-1] for a in authors]
            author_str = first_names[0]
            if len(first_names) > 1:
                author_str += f", {' & '.join(first_names[1:])}"
            if len(authors) > 2:
                author_str += ", et al."
        else:
            author_str = "Unknown"

        return f"{author_str} ({year}). {title}."

    @staticmethod
    def format_markdown(paper: dict) -> str:
        """
        Format paper info for markdown.

        Args:
            paper: Paper dictionary

        Returns:
            Markdown formatted paper entry
        """
        title = paper.get("title", "Unknown")
        authors = paper.get("authors", [])
        year = paper.get("year", "")
        url = paper.get("url", "")

        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += ", et al."

        if url:
            return f"- **{title}** ({author_str}, {year}) [[PDF]]({url})"

        return f"- **{title}** ({author_str}, {year})"


formatter = CitationFormatter()
