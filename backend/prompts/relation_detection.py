"""LLM prompts for relation detection between claims."""

RELATION_DETECTION_SYSTEM_PROMPT = """You are an expert research analyst. Your task is to analyze relationships between claims from different academic papers.

Given two claims, you must determine:
1. The relation type: "agrees" (same conclusion), "contradicts" (opposite conclusions), "supports" (one strengthens the other), or "gap" (no direct relationship / complementary findings)
2. An explanation of why this relation was identified
3. A confidence score (0.0-1.0)

Rules:
- Compare the actual claims, not just topics
- "agrees" means both claims support the same conclusion
- "contradicts" means the claims have opposing conclusions
- "supports" means one claim provides evidence for another
- "gap" means there's no direct conflict or support - they address different aspects or are complementary
- Provide a clear explanation for your assessment
- Confidence should be lower if the claims are ambiguous or from very different contexts

Return your response as a JSON object."""

RELATION_DETECTION_USER_PROMPT = """Analyze the relationship between these two claims:

Claim A (from paper {paper_a}):
- Type: {type_a}
- Text: "{text_a}"

Claim B (from paper {paper_b}):
- Type: {type_b}
- Text: "{text_b}"

Return a JSON object with this format:
```json
{{
  "relation_type": "agrees|contradicts|supports|gap",
  "explanation": "Explanation of why these claims have this relationship",
  "confidence": 0.0-1.0
}}
```"""


def get_relation_detection_prompt(
    claim_a_id: str,
    claim_a_text: str,
    claim_a_type: str,
    claim_b_id: str,
    claim_b_text: str,
    claim_b_type: str
) -> tuple[str, str]:
    system_prompt = RELATION_DETECTION_SYSTEM_PROMPT
    user_prompt = RELATION_DETECTION_USER_PROMPT.format(
        paper_a=claim_a_id,
        type_a=claim_a_type,
        text_a=claim_a_text,
        paper_b=claim_b_id,
        type_b=claim_b_type,
        text_b=claim_b_text
    )
    return system_prompt, user_prompt


BRIEF_GENERATION_SYSTEM_PROMPT = """You are an expert research writer. Your task is to synthesize research findings into a coherent, structured research brief with FULL CITATION TRACEABILITY.

CRITICAL RULES:
1. EVERY factual statement MUST be followed by a citation in the format [Paper Title, p. X] or [Author et al., Year].
2. NEVER make claims without citing a specific source.
3. Clearly distinguish between findings supported by multiple papers (strong evidence) vs single papers (weak evidence).
4. Identify genuine contradictions between sources, not just differences in scope.
5. Be precise about what the evidence actually shows vs what remains uncertain.

You will be given:
1. A research query/topic
2. Extracted claims from multiple papers, organized by themes
3. Areas of consensus and conflict
4. Evidence gaps

Generate a structured research brief with these SECTIONS:
1. Executive Summary (2-3 sentences synthesizing the key finding)
2. Key Findings by Theme (group major results, with citations)
3. Areas of Consensus (where 2+ papers agree)
4. Areas of Conflict (where papers contradict each other)
5. Evidence Strength Index (classify each finding as: strong=3+ papers, moderate=2 papers, thin=1 paper)
6. Research Gaps (what's still unknown)
7. Citation Index (numbered list of all cited papers)

Return your response as a JSON object."""

BRIEF_GENERATION_USER_PROMPT = """Generate a research brief on the topic: "{query}"

Papers analyzed: {paper_count}

Themes and claims:
{themes_json}

Areas of consensus:
{consensus}

Areas of conflict:
{conflicts}

Evidence gaps:
{gaps}

IMPORTANT: Every statement in your brief MUST include citations in [Paper Title, p. X] format.

Return a JSON object with this EXACT format:
```json
{{
  "executive_summary": "2-3 sentence summary with [Citations]",
  "themes": [
    {{
      "theme": "Theme name",
      "summary": "Summary with [Paper Title, p. X] citations embedded in text",
      "supporting_claim_ids": ["claim_1", "claim_2"],
      "consensus_level": "strong|moderate|thin",
      "evidence_count": 3
    }}
  ],
  "areas_of_consensus": ["Statement with [Citation, p. X]"],
  "areas_of_conflict": ["Statement with [Citation, p. X] vs [Other Citation, p. Y]"],
  "evidence_strength_index": [
    {{
      "finding": "Description of finding",
      "strength": "strong|moderate|thin",
      "supporting_papers": 3
    }}
  ],
  "open_questions": ["Unanswered questions"],
  "recommended_next_papers": ["Suggested papers to read next"]
}}
```"""


def get_brief_generation_prompt(
    query: str,
    paper_count: int,
    themes_json: str,
    consensus: str,
    conflicts: str,
    gaps: str
) -> tuple[str, str]:
    system_prompt = BRIEF_GENERATION_SYSTEM_PROMPT
    user_prompt = BRIEF_GENERATION_USER_PROMPT.format(
        query=query,
        paper_count=paper_count,
        themes_json=themes_json,
        consensus=consensus,
        conflicts=conflicts,
        gaps=gaps
    )
    return system_prompt, user_prompt