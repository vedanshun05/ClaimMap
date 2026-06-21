"""Claim extraction module with async parallel processing, robust JSON parsing, and retry."""

import sys
import os
from pathlib import Path
import json
import re
import asyncio
import logging
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from prompts import get_claim_extraction_prompt, get_strict_claim_extraction_prompt

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RATE_LIMIT_DELAY = 0.3
MAX_CHARS_PER_SECTION = 3000
MIN_SECTION_LENGTH = 300
MAX_SECTIONS_PER_PAPER = 8
MAX_CONCURRENT_LLM = 3

_LLM_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_LLM)
_ENV_LOADED = False


def _load_env_once():
    global _ENV_LOADED
    if not _ENV_LOADED:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent.parent / ".env", override=False)
        load_dotenv(Path(__file__).parent.parent / ".env", override=False)
        _ENV_LOADED = True


def extract_json_array(text: str) -> list[dict]:
    """Robust JSON array extraction with 3-level fallback strategy."""
    text = text.strip()

    stripped = _strip_code_fences(text)
    try:
        result = json.loads(stripped)
        if isinstance(result, list):
            return [r for r in result if isinstance(r, dict)]
        if isinstance(result, dict):
            return [result]
    except (json.JSONDecodeError, TypeError):
        pass

    bracket_content = _extract_bracket_content(stripped)
    if bracket_content:
        try:
            result = json.loads(bracket_content)
            if isinstance(result, list):
                return [r for r in result if isinstance(r, dict)]
        except (json.JSONDecodeError, TypeError):
            pass

    objects = _extract_json_objects(stripped)
    if objects:
        return objects

    return []


def _strip_code_fences(text: str) -> str:
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = text.replace('```', '')
    return text.strip()


def _extract_bracket_content(text: str) -> Optional[str]:
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return None


def _extract_json_objects(text: str) -> list[dict]:
    objects = []
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    for match in re.finditer(pattern, text):
        try:
            obj = json.loads(match.group())
            if isinstance(obj, dict):
                objects.append(obj)
        except (json.JSONDecodeError, TypeError):
            continue
    return objects


def _process_claims(claims_data: list[dict], section_name: str, page_number: int) -> list[dict]:
    """Process raw claim dicts, enforcing required fields."""
    VALID_TYPES = {"finding", "hypothesis", "limitation"}
    claims = []
    for item in claims_data:
        if not isinstance(item, dict):
            continue
        text = item.get("text", "").strip()
        if not text:
            continue
        claim_type = item.get("claim_type", "finding").lower()
        if claim_type not in VALID_TYPES:
            claim_type = "finding"
        claims.append({
            "claim_type": claim_type,
            "text": text,
            "source_section": section_name,
            "source_sentence": item.get("source_sentence", text[:200]),
            "page_number": item.get("page_number", page_number),
            "confidence": min(1.0, max(0.0, float(item.get("confidence", 0.8)))),
            "is_validated": False,
        })
    return claims


OPENCODE_API_BASE = "https://opencode.ai/zen/v1"


async def _call_llm_async(system_prompt: str, user_prompt: str, max_retries: int = MAX_RETRIES) -> Optional[str]:
    """Async LLM call with semaphore-limited concurrency, retry, and rate-limit handling."""
    import os

    async with _LLM_SEMAPHORE:
        for attempt in range(max_retries):
            try:
                import litellm

                model = os.getenv("DEFAULT_MODEL", "openai/deepseek-v4-flash-free")
                api_key = os.getenv("OPENCODE_API_KEY")

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                response = await litellm.acompletion(
                    model=model,
                    api_base=OPENCODE_API_BASE,
                    api_key=api_key,
                    messages=messages,
                    temperature=0.1
                )

                return response.choices[0].message.content

            except Exception as e:
                error_str = str(e)
                logger.warning(f"[ClaimExtractor] LLM attempt {attempt + 1} failed: {e}")

                if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
                    wait_time = 5 * (attempt + 1)
                    logger.info(f"Rate limited, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue

                if attempt < max_retries - 1:
                    await asyncio.sleep(1.5 ** attempt)
                    continue

                logger.error(f"[ClaimExtractor] All {max_retries} LLM attempts failed")
                return None

        return None


async def _extract_from_section_async(section_content: str, section_name: str, page_number: int) -> list[dict]:
    """Extract claims from a single section with retry on empty results."""
    if not section_content or len(section_content) < MIN_SECTION_LENGTH:
        return []

    truncated = section_content[:MAX_CHARS_PER_SECTION]

    system_prompt, user_prompt = get_claim_extraction_prompt(
        section_name=section_name,
        section_content=truncated,
        page_number=page_number
    )

    raw = await _call_llm_async(system_prompt, user_prompt)
    if not raw:
        return []

    claims_data = extract_json_array(raw)
    claims = _process_claims(claims_data, section_name, page_number)

    if claims:
        return claims

    logger.info(f"[ClaimExtractor] Retrying with strict prompt for section '{section_name}'")
    system_prompt2, user_prompt2 = get_strict_claim_extraction_prompt(
        section_name=section_name,
        section_content=truncated,
        page_number=page_number
    )

    raw2 = await _call_llm_async(system_prompt2, user_prompt2)
    if not raw2:
        return []

    claims_data2 = extract_json_array(raw2)
    return _process_claims(claims_data2, section_name, page_number)


async def extract_claims_async(paper_id: str, sections: list[dict]) -> list[dict]:
    """Async parallel claim extraction from paper sections.

    Filters out short sections, prioritizes content-rich ones,
    and runs up to MAX_CONCURRENT_LLM calls in parallel.
    """
    _load_env_once()

    candidates = []
    for section in sections:
        heading = section.get("heading", "")
        content = section.get("content", "")
        page = section.get("page_number", 0)
        if heading and content and len(content) >= MIN_SECTION_LENGTH:
            candidates.append((content, heading, page))

    candidates.sort(key=lambda x: len(x[0]), reverse=True)
    candidates = candidates[:MAX_SECTIONS_PER_PAPER]

    if not candidates:
        return []

    tasks = [
        _extract_from_section_async(content, heading, page)
        for content, heading, page in candidates
    ]

    logger.info(f"[ClaimExtractor] Extracting claims from {len(tasks)} sections in parallel (max {MAX_CONCURRENT_LLM} concurrent)")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_claims = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"[ClaimExtractor] Section {candidates[i][1]} failed: {result}")
            continue
        if isinstance(result, list):
            for claim in result:
                claim["paper_id"] = paper_id
            all_claims.extend(result)

    return all_claims


class ClaimExtractor:
    """Synchronous wrapper for backward compatibility."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def extract_from_section(self, section_content: str, section_name: str, page_number: int = 0) -> list[dict]:
        if not section_content or len(section_content) < MIN_SECTION_LENGTH:
            return []

        truncated = section_content[:MAX_CHARS_PER_SECTION]
        system_prompt, user_prompt = get_claim_extraction_prompt(
            section_name=section_name, section_content=truncated, page_number=page_number
        )

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                logger.warning("[ClaimExtractor] Cannot run async extraction from sync context with running loop")
                return []
        except RuntimeError:
            pass

        return asyncio.run(
            _extract_from_section_async(truncated, section_name, page_number)
        )

    def extract_from_paper(self, paper_id: str, sections: list[dict]) -> list[dict]:
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, extract_claims_async(paper_id, sections))
                    return future.result(timeout=300)
        except RuntimeError:
            pass

        return asyncio.run(extract_claims_async(paper_id, sections))


extractor = ClaimExtractor()
