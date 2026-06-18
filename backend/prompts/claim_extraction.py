"""LLM prompts for claim extraction."""

CLAIM_EXTRACTION_SYSTEM_PROMPT = """You are an expert research analyst. Your task is to extract specific factual claims from academic paper sections.

For each claim, you must identify:
1. The claim type: "finding" (proven result), "hypothesis" (proposed but not proven), or "limitation" (acknowledged weakness)
2. The exact claim text (verbatim from the section)
3. The source section name
4. The exact source sentence containing the claim
5. A confidence score (0.0-1.0)

Rules:
- Extract ONLY verbatim claims from the text
- Do NOT hallucinate or infer claims not present in the text
- Distinguish between findings (proven results), hypotheses (proposed but not proven), and limitations (acknowledged weaknesses)
- If text is ambiguous, mark the claim type as "hypothesis" rather than "finding"
- Provide the exact source sentence where the claim appears
- Be precise about which section the claim comes from

Return your response as a JSON array of claim objects."""

CLAIM_EXTRACTION_USER_PROMPT = """Extract claims from this paper section:

Section: {section_name}
Page: {page_number}

Content:
{section_content}

Return a JSON array of claim objects with this format:
```json
[
  {{
    "claim_type": "finding|hypothesis|limitation",
    "text": "The exact claim from the paper",
    "source_section": "{section_name}",
    "source_sentence": "The exact sentence containing the claim",
    "page_number": {page_number},
    "confidence": 0.0-1.0
  }}
]
```

Only extract significant claims that convey new knowledge, insights, or acknowledged limitations. Ignore generic statements."""

CLAIM_EXTRACTION_STRICT_SYSTEM_PROMPT = """You are a strict research claim extractor. You MUST extract claims from the given text.

CRITICAL RULES:
1. Return ONLY a valid JSON array. No markdown, no commentary, no explanation.
2. Each claim MUST have: "text" (exact quote), "claim_type" (finding/hypothesis/limitation), "source_sentence" (verbatim from text), "page_number" (integer), "confidence" (0.0-1.0).
3. If you cannot find claims, return an empty array: []
4. Do NOT invent or paraphrase claims. Use EXACT text from the section.
5. The "source_sentence" field MUST contain text that appears verbatim in the section content.

Output format: JSON array only."""

CLAIM_EXTRACTION_STRICT_USER_PROMPT = """Extract factual claims from this section. Output ONLY a valid JSON array.

Section: {section_name} | Page: {page_number}

Content:
{section_content}

Required JSON format:
[{{"claim_type":"finding|hypotesis|limitation","text":"exact quote","source_section":"{section_name}","source_sentence":"verbatim sentence from content","page_number":{page_number},"confidence":0.8}}]

If no verifiable claims exist, return: []"""


def get_claim_extraction_prompt(section_name: str, section_content: str, page_number: int = 0) -> tuple[str, str]:
    system_prompt = CLAIM_EXTRACTION_SYSTEM_PROMPT
    user_prompt = CLAIM_EXTRACTION_USER_PROMPT.format(
        section_name=section_name,
        section_content=section_content[:MAX_CHARS_PER_SECTION] if len(section_content) > MAX_CHARS_PER_SECTION else section_content,
        page_number=page_number
    )
    return system_prompt, user_prompt


def get_strict_claim_extraction_prompt(section_name: str, section_content: str, page_number: int = 0) -> tuple[str, str]:
    system_prompt = CLAIM_EXTRACTION_STRICT_SYSTEM_PROMPT
    user_prompt = CLAIM_EXTRACTION_STRICT_USER_PROMPT.format(
        section_name=section_name,
        section_content=section_content[:MAX_CHARS_PER_SECTION] if len(section_content) > MAX_CHARS_PER_SECTION else section_content,
        page_number=page_number
    )
    return system_prompt, user_prompt


MAX_CHARS_PER_SECTION = 3000