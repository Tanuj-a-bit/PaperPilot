"""Semantic Scholar API client with rate-limit tolerance and optional API key.
Searches across IEEE, ACM, Springer, Nature, arXiv, etc.
Zero local storage.
"""

import os
import requests

SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def query_semantic_scholar_live(query: str, max_results: int = 7) -> list[dict]:
    """
    Search Semantic Scholar for papers across publishers (IEEE, arXiv, ACM, etc.).
    Gracefully returns empty list if rate-limited so fallback (OpenAlex) handles it.
    """
    params = {
        "query": query,
        "limit": min(max_results, 20),
        "fields": "title,authors,year,abstract,url,venue,publicationVenue,openAccessPdf,externalIds"
    }
    headers = {
        "User-Agent": "PaperPilot/2.0 (academic-research-assistant)"
    }
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    
    try:
        response = requests.get(SEMANTIC_SCHOLAR_SEARCH_URL, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        papers = []
        for item in data.get("data", []):
            abstract = item.get("abstract") or "No abstract provided."
            authors_list = [a.get("name") for a in item.get("authors", []) if a.get("name")]
            authors_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "") if authors_list else "Unknown Authors"
            year = str(item.get("year")) if item.get("year") else "Recent"
            venue = item.get("venue") or ""
            if not venue and item.get("publicationVenue"):
                venue = item.get("publicationVenue", {}).get("name", "")
            
            ext_ids = item.get("externalIds") or {}
            source_tag = "Semantic Scholar"
            if "DOI" in ext_ids and "10.1109" in ext_ids["DOI"]:
                source_tag = "IEEE"
            elif venue and "ieee" in venue.lower():
                source_tag = "IEEE"
            elif "ArXiv" in ext_ids:
                source_tag = "arXiv"
            elif venue:
                source_tag = venue[:25]
                
            pdf_url = ""
            if item.get("openAccessPdf"):
                pdf_url = item["openAccessPdf"].get("url", "")
            if not pdf_url:
                pdf_url = item.get("url") or (f"https://doi.org/{ext_ids['DOI']}" if "DOI" in ext_ids else "")

            identifier = ext_ids.get("DOI") or ext_ids.get("ArXiv") or item.get("paperId", "")[:12]

            papers.append({
                "id": identifier,
                "title": item.get("title", "Untitled").strip(),
                "authors": authors_str,
                "year": year,
                "summary": abstract.strip(),
                "venue": venue or "Academic Conference/Journal",
                "source": source_tag,
                "pdf_url": pdf_url,
                "arxiv_id": ext_ids.get("ArXiv", "")
            })
        return papers
    except Exception:
        return []
