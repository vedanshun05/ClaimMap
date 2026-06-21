"""LLM client for claim extraction using litellm."""

import os
import json
from typing import Any

from src.shared.config import config, api_config


class LLMClient:
    """Client for LLM calls via litellm."""

    def __init__(self, model: str | None = None):
        self.model = model or config.default_model or "nvidia/nim/gemini-2.0-flash"
        self._client = None

    def _get_client(self):
        """Get or create litellm client."""
        if self._client is None:
            try:
                import litellm
                litellm.drop_params = True
                self._client = litellm
            except ImportError:
                raise ImportError("litellm not installed. Run: pip install litellm")

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        """
        Generate text from LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional litellm parameters

        Returns:
            Generated text
        """
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        api_key = api_config.get_litellm_key()
        if api_key:
            os.environ["NVIDIA_API_KEY"] = api_key

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content
        except AttributeError:
            try:
                response = client.completion(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLM Client] Error: {e}")
                return ""
        except Exception as e:
            print(f"[LLM Client] Error: {e}")
            return ""

    def generate_json(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any] | None:
        """
        Generate JSON from LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional litellm parameters

        Returns:
            Parsed JSON response, or None if parsing fails
        """
        text = self.generate(prompt, system_prompt, **kwargs)

        if not text:
            return None

        json_str = self._extract_json(text)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"[LLM Client] JSON parse error: {e}")
                return None

        return None

    def _extract_json(self, text: str) -> str | None:
        """Extract JSON from text that may contain markdown code blocks."""
        text = text.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            json_lines = []
            in_json = False

            for line in lines:
                if line.startswith("```"):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)

            if json_lines:
                return "\n".join(json_lines)

        if text.startswith("{"):
            return text

        return None


class ClaimExtractionPrompt:
    """Prompt templates for claim extraction."""

    SYSTEM_PROMPT = """You are an expert research analyst. Your task is to extract specific factual claims from academic papers.

For each claim, you must identify:
1. The claim type: "finding", "hypothesis", or "limitation"
2. The exact claim text (verbatim from the paper)
3. The source section (e.g., "Results", "Discussion")
4. A location reference (e.g., "page 5, paragraph 2")

Rules:
- Extract ONLY verbatim claims from the text
- Do NOT hallucinate or infer claims not present in the text
- Distinguish between findings (proven results), hypotheses (proposed but not proven), and limitations (acknowledged weaknesses)
- If text is ambiguous, mark the claim type as "hypothesis" rather than "finding"
- Be precise with location references

Return your response as a JSON array of claim objects."""

    USER_PROMPT_TEMPLATE = """Extract claims from the following paper text:

Title: {title}

Text:
{paper_text}

Return a JSON array with up to {max_claims} claims in this format:
```json
[
  {{
    "claim_type": "finding|hypothesis|limitation",
    "claim_text": "The exact claim from the paper",
    "source_section": "Section name",
    "source_location": "Approximate location",
    "confidence": 0.0-1.0
  }}
]
```

Only extract significant claims that convey new knowledge or insights."""


def extract_claims_from_text(
    text: str,
    title: str,
    llm_client: LLMClient | None = None,
    max_claims: int = 20,
) -> list[dict]:
    """
    Extract claims from paper text using LLM.

    Args:
        text: Paper text content
        title: Paper title
        llm_client: LLM client instance
        max_claims: Maximum number of claims to extract

    Returns:
        List of claim dictionaries
    """
    if llm_client is None:
        llm_client = LLMClient()

    prompt = ClaimExtractionPrompt.USER_PROMPT_TEMPLATE.format(
        title=title,
        paper_text=text[:15000],
        max_claims=max_claims,
    )

    result = llm_client.generate_json(
        prompt=prompt,
        system_prompt=ClaimExtractionPrompt.SYSTEM_PROMPT,
        temperature=0.1,
    )

    if result and isinstance(result, list):
        return result

    return []
