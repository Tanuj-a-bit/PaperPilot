"""On-the-fly academic reasoning features powered directly by arXiv API + Gemini.
Zero database, zero vector storage, zero disk saving.
"""

from src.llm.gemini_client import generate
from src.apis.arxiv_client import query_arxiv_live

def live_arxiv_qa(question: str, topic: str = "") -> dict:
    """
    1. Calls arXiv API live on-the-fly for relevant papers matching the question/topic.
    2. Streams retrieved paper abstracts directly into Gemini's context window.
    3. Returns citation-grounded answer.
    """
    search_term = topic if topic.strip() else question
    live_papers = query_arxiv_live(search_term, max_results=6)
    
    if not live_papers:
        return {
            "answer": f"No papers found on arXiv for query '{search_term}'.",
            "papers": []
        }
        
    papers_context = ""
    for idx, p in enumerate(live_papers):
        papers_context += f"\n[Paper {idx+1}] {p['title']} ({p['year']}) | arXiv ID: {p['arxiv_id']}\n"
        papers_context += f"Authors: {p['authors']}\n"
        papers_context += f"Abstract: {p['summary']}\n"
        
    prompt = f"""You are PaperPilot, an academic research assistant powered by the arXiv API and Gemini.
Answer the user's question using ONLY the live papers fetched from arXiv below.

RULES:
1. Always cite exact paper titles and arXiv IDs for every factual statement: [Paper Title, arXiv:ID].
2. If the papers don't provide sufficient evidence to answer completely, explicitly mention what is missing.
3. Distinguish between empirical results and theoretical claims.

Live arXiv Papers:
{papers_context}

User Question:
{question}
"""
    answer = generate(prompt)
    return {
        "answer": answer,
        "papers": live_papers
    }


def live_compare_arxiv(selected_papers: list[dict]) -> str:
    """Performs real-time comparative analysis directly from arXiv metadata."""
    if len(selected_papers) < 2:
        return "Please select at least 2 papers to compare."
        
    context = ""
    for idx, p in enumerate(selected_papers):
        context += f"\n--- PAPER {idx+1}: {p['title']} ({p['year']}) [arXiv:{p['arxiv_id']}] ---\n"
        context += f"Authors: {p['authors']}\n"
        context += f"Abstract: {p['summary']}\n"
        
    prompt = f"""Compare the following research papers live from arXiv across these dimensions:
1. Core Objective / Problem Addressed
2. Proposed Method & Architecture
3. Benchmark / Evaluation Focus
4. Key Findings & Contributions
5. Stated or Inherent Limitations

Format as a structured markdown comparative matrix, followed by key takeaways.
Never invent details not present in the papers. If not found, write "Not mentioned in abstract".

Papers:
{context}
"""
    return generate(prompt)


def live_research_gaps(topic: str, live_papers: list[dict]) -> str:
    """Discovers recurring limitations and PhD research gaps from live arXiv query."""
    context = ""
    for idx, p in enumerate(live_papers):
        context += f"\n- {p['title']} ({p['year']}) [arXiv:{p['arxiv_id']}]:\n  {p['summary']}\n"
        
    prompt = f"""You are an elite PhD Academic Advisor.
Based on these live arXiv papers retrieved for "{topic}":
{context}

Analyze the cross-paper limitations and suggest 3 high-impact PhD Research Gaps:
For each gap:
1. **Gap Title**
2. **Current Failure Mode / Limitation in literature** (cite specific arXiv papers)
3. **Proposed Novel PhD Direction**
4. **Viable Methodology & Expected Contribution**
"""
    return generate(prompt)
