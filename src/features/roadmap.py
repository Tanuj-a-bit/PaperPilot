"""PhD Research Roadmap Generator.
Transforms literature search results into an evolutionary, pedagogical PhD reading path.
"""

import json
from src.llm.gemini_client import generate

def generate_phd_roadmap(topic: str, papers: list[dict]) -> dict:
    """
    Takes fetched paper metadata and organizes them into 4 structured PhD stages:
    1. Foundations (Prerequisites / Seminal papers)
    2. Core Paradigms (Foundational frameworks establishing the field)
    3. Advanced & Recent Extensions (SOTA improvements)
    4. Frontier & Open Research Gaps (Unsolved PhD-level directions)
    """
    if not papers:
        return {}

    papers_info = []
    for idx, p in enumerate(papers):
        papers_info.append({
            "index": idx,
            "title": p.get("title"),
            "year": p.get("year"),
            "authors": p.get("authors"),
            "summary": p.get("summary", "")[:400]
        })
    
    prompt = f"""You are an elite PhD Academic Advisor and Principal Research Scientist.
You are designing a structured, step-by-step reading and literature mastery roadmap on the topic: "{topic}".

Below is a curated set of papers retrieved for this domain:
{json.dumps(papers_info, indent=2)}

Organize these papers and the domain into a comprehensive 4-stage PhD literature roadmap. 
Return ONLY valid JSON with this exact schema:
{{
  "topic": "{topic}",
  "executive_summary": "Short 2-sentence description of the learning progression",
  "stages": [
    {{
      "stage_number": 1,
      "stage_name": "Stage 1: Foundations & Prerequisites",
      "stage_goal": "What a researcher should understand after this stage",
      "papers": [
        {{
          "title": "Exact Title of Paper from the list or seminal domain prerequisite",
          "year": "Year",
          "why_read": "Why this paper is indispensable first",
          "key_takeaway": "Key theoretical contribution or breakthrough"
        }}
      ]
    }},
    {{
      "stage_number": 2,
      "stage_name": "Stage 2: Core Architectures & Methods",
      "stage_goal": "Mastering the foundational standards and baselines",
      "papers": [ ... ]
    }},
    {{
      "stage_number": 3,
      "stage_name": "Stage 3: SOTA Advances & Optimization",
      "stage_goal": "Deep dive into recent enhancements and specialized variants",
      "papers": [ ... ]
    }},
    {{
      "stage_number": 4,
      "stage_name": "Stage 4: Open Frontier & PhD Research Gaps",
      "stage_goal": "Synthesizing unsolved problems for thesis exploration",
      "research_gaps": [
        {{
          "gap_title": "Title of the open research gap",
          "problem_statement": "Description of why existing methods fail here",
          "suggested_approach": "Hypothesis or experimental design for a PhD scholar"
        }}
      ]
    }}
  ]
}}

Ensure every paper selected from the provided list is categorized logically according to chronological depth and conceptual dependency. Return only pure JSON (no markdown formatting, no code ticks).
"""
    raw_response = generate(prompt)
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback if model wraps in extra text
        import re
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {
            "topic": topic,
            "executive_summary": "Auto-generated PhD reading path.",
            "stages": []
        }
