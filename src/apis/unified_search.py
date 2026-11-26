"""Unified paper search engine combining arXiv, Semantic Scholar, and OpenAlex.
Provides multi-source academic coverage (IEEE, ACM, Nature, Springer, arXiv, etc.).
Zero local storage.
"""

from src.apis.arxiv_client import query_arxiv_live
from src.apis.semantic_scholar_client import query_semantic_scholar_live
from src.apis.openalex_client import query_openalex_live

def search_academic_papers(query: str, source: str = "all", max_results: int = 8) -> list[dict]:
    """
    Query academic literature across selectable providers:
    - 'all': Aggregates from OpenAlex (IEEE, journals) + arXiv (preprints) + Semantic Scholar
    - 'arxiv': arXiv preprints
    - 'openalex': OpenAlex global index (IEEE, Springer, Elsevier, etc.)
    - 'semanticscholar': Semantic Scholar
    """
    source = (source or "all").lower().strip()
    
    if source == "arxiv":
        raw = query_arxiv_live(query, max_results=max_results)
        return [{
            "id": p.get("arxiv_id") or p.get("title", "")[:15],
            "title": p.get("title", ""),
            "authors": p.get("authors", ""),
            "year": p.get("year", ""),
            "summary": p.get("summary", ""),
            "venue": "arXiv Preprint",
            "source": "arXiv",
            "pdf_url": p.get("pdf_url", ""),
            "arxiv_id": p.get("arxiv_id", "")
        } for p in raw]

    if source == "openalex":
        return query_openalex_live(query, max_results=max_results)

    if source == "semanticscholar":
        return query_semantic_scholar_live(query, max_results=max_results)

    # If "all": Aggregate OpenAlex (which reliably indexes IEEE & major publishers) + arXiv + Semantic Scholar
    results = []
    seen_titles = set()

    # 1. Fetch from OpenAlex (great for IEEE, ACM, Springer, Nature without aggressive rate limits)
    oa_papers = query_openalex_live(query, max_results=max_results)
    for p in oa_papers:
        clean_t = "".join(filter(str.isalnum, p["title"].lower()))
        if clean_t and clean_t not in seen_titles:
            seen_titles.add(clean_t)
            results.append(p)

    # 2. Fetch from arXiv (latest CS/AI preprints)
    arxiv_papers = query_arxiv_live(query, max_results=max_results)
    for p in arxiv_papers:
        clean_t = "".join(filter(str.isalnum, p["title"].lower()))
        if clean_t and clean_t not in seen_titles:
            seen_titles.add(clean_t)
            results.append({
                "id": p.get("arxiv_id") or clean_t[:15],
                "title": p.get("title", ""),
                "authors": p.get("authors", ""),
                "year": p.get("year", ""),
                "summary": p.get("summary", ""),
                "venue": "arXiv Preprint",
                "source": "arXiv",
                "pdf_url": p.get("pdf_url", ""),
                "arxiv_id": p.get("arxiv_id", "")
            })

    # 3. Fill from Semantic Scholar if available
    s2_papers = query_semantic_scholar_live(query, max_results=max_results)
    for p in s2_papers:
        clean_t = "".join(filter(str.isalnum, p["title"].lower()))
        if clean_t and clean_t not in seen_titles:
            seen_titles.add(clean_t)
            results.append(p)

    return results[:max_results]
