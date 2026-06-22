import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ProjectConfig:
    """Project-wide configuration."""

    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(init=False)
    output_dir: Path = field(init=False)

    # API Settings
    # Default OpenAI chat model for both CLI pipeline and backend
    default_model: str = field(default="gpt-4.1-mini")
    max_papers_per_query: int = 20

    # File names for pipeline
    discovered_papers_file: str = "discovered_papers.json"
    ingested_papers_file: str = "ingested_papers.json"
    extracted_claims_file: str = "extracted_claims.json"
    synthesis_file: str = "synthesis.json"
    brief_md_file: str = "research_brief.md"
    brief_pdf_file: str = "research_brief.pdf"

    def __post_init__(self):
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)


@dataclass
class APIConfig:
    """API configuration for LLM providers."""

    opencode_api_key: str | None = field(default_factory=lambda: os.getenv("OPENCODE_API_KEY"))
    semantic_scholar_api_key: str | None = field(default_factory=lambda: os.getenv("SEMANTIC_SCHOLAR_API_KEY"))

    def get_api_key(self) -> str | None:
        """Return the OpenCode Zen API key."""
        return self.opencode_api_key


config = ProjectConfig()
api_config = APIConfig()
