"""Relation detector - detects relationships between claims."""

import sys
from pathlib import Path
import json
import asyncio
import os
import logging
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from prompts import get_relation_detection_prompt

logger = logging.getLogger(__name__)

MAX_CONCURRENT_RELATIONS = 5


class RelationDetector:
    """Detects relationships between pairs of claims using LLM."""

    def __init__(self, llm_client=None):
        """
        Initialize relation detector.

        Args:
            llm_client: LLM client for generating responses
        """
        self.llm_client = llm_client

    async def _get_llm_response_async(self, system_prompt: str, user_prompt: str) -> Optional[dict]:
        """Get LLM response (async, non-blocking)."""
        if self.llm_client:
            return self.llm_client.generate_json(user_prompt, system_prompt)

        try:
            import litellm
            from dotenv import load_dotenv

            load_dotenv()

            api_key = os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                os.environ["NVIDIA_API_KEY"] = api_key

            model = os.getenv("DEFAULT_MODEL", "nvidia_nim/meta/llama-3.1-8b-instruct")


            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=0.1
            )

            text = response.choices[0].message.content
            return self._parse_json_response(text)

        except Exception as e:
            logger.warning(f"[RelationDetector] LLM error: {e}")
            return None

    def _get_llm_response(self, system_prompt: str, user_prompt: str) -> Optional[dict]:
        """Synchronous fallback for backward compatibility."""
        try:
            return asyncio.run(self._get_llm_response_async(system_prompt, user_prompt))
        except RuntimeError:
            # Already in an event loop — use thread fallback
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self._get_llm_response_async(system_prompt, user_prompt)
                )
                return future.result(timeout=60)

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """Parse JSON from LLM response."""
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
                text = "\n".join(json_lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    async def compare_async(self, claim_a: dict, claim_b: dict) -> Optional[dict]:
        """
        Compare two claims and determine their relationship (async).

        Args:
            claim_a: First claim dict
            claim_b: Second claim dict

        Returns:
            Relation dict with relation_type, explanation, confidence
        """
        system_prompt, user_prompt = get_relation_detection_prompt(
            claim_a_id=claim_a.get("id", claim_a.get("paper_id", "unknown")),
            claim_a_text=claim_a.get("text", ""),
            claim_a_type=claim_a.get("claim_type", "finding"),
            claim_b_id=claim_b.get("id", claim_b.get("paper_id", "unknown")),
            claim_b_text=claim_b.get("text", ""),
            claim_b_type=claim_b.get("claim_type", "finding")
        )

        response = await self._get_llm_response_async(system_prompt, user_prompt)

        if response and "relation_type" in response:
            return {
                "relation_type": response.get("relation_type", "gap"),
                "explanation": response.get("explanation", ""),
                "confidence": response.get("confidence", 0.5)
            }

        return None

    def compare(self, claim_a: dict, claim_b: dict) -> Optional[dict]:
        """Synchronous compare (backward compat). Prefer compare_async."""
        system_prompt, user_prompt = get_relation_detection_prompt(
            claim_a_id=claim_a.get("id", claim_a.get("paper_id", "unknown")),
            claim_a_text=claim_a.get("text", ""),
            claim_a_type=claim_a.get("claim_type", "finding"),
            claim_b_id=claim_b.get("id", claim_b.get("paper_id", "unknown")),
            claim_b_text=claim_b.get("text", ""),
            claim_b_type=claim_b.get("claim_type", "finding")
        )

        response = self._get_llm_response(system_prompt, user_prompt)

        if response and "relation_type" in response:
            return {
                "relation_type": response.get("relation_type", "gap"),
                "explanation": response.get("explanation", ""),
                "confidence": response.get("confidence", 0.5)
            }

        return None

    async def compare_group_async(self, claims: list[dict]) -> list[dict]:
        """
        Compare all pairs of claims within a group (async, concurrent).

        Runs comparisons concurrently with a semaphore to limit parallelism.
        Skips pairs from the same paper.

        Args:
            claims: List of claims to compare

        Returns:
            List of relation dicts
        """
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_RELATIONS)
        pairs = []

        for i, claim_a in enumerate(claims):
            for claim_b in claims[i + 1:]:
                if claim_a.get("paper_id") == claim_b.get("paper_id"):
                    continue
                pairs.append((claim_a, claim_b))

        if not pairs:
            return []

        logger.info(f"[RelationDetector] Comparing {len(pairs)} claim pairs concurrently (max {MAX_CONCURRENT_RELATIONS})")

        async def _compare_with_semaphore(ca, cb):
            async with semaphore:
                return (ca, cb, await self.compare_async(ca, cb))

        results = await asyncio.gather(
            *[_compare_with_semaphore(ca, cb) for ca, cb in pairs],
            return_exceptions=True
        )

        relations = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"[RelationDetector] Comparison failed: {result}")
                continue
            claim_a, claim_b, relation = result
            if relation:
                relation["claim_ids"] = [
                    str(claim_a.get("id", claim_a.get("paper_id", "unknown"))),
                    str(claim_b.get("id", claim_b.get("paper_id", "unknown")))
                ]
                relations.append(relation)

        return relations

    def compare_group(self, claims: list[dict]) -> list[dict]:
        """Synchronous compare_group (backward compat). Prefer compare_group_async."""
        relations = []

        for i, claim_a in enumerate(claims):
            for claim_b in claims[i + 1:]:
                if claim_a.get("paper_id") == claim_b.get("paper_id"):
                    continue

                relation = self.compare(claim_a, claim_b)

                if relation:
                    relation["claim_ids"] = [
                        str(claim_a.get("id", claim_a.get("paper_id", "unknown"))),
                        str(claim_b.get("id", claim_b.get("paper_id", "unknown")))
                    ]
                    relations.append(relation)

        return relations


detector = RelationDetector()
