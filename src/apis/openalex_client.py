"""OpenAlex API client.
Searches over 250M scholarly works worldwide, including IEEE, Springer, Elsevier, arXiv.
Free, open, no API key required.
Zero local storage.
"""

import requests

OPENALEX_WORKS_URL = "https://api.openalex.org/works"

def query_openalex_live(query: str, max_results: int = 7) -> list[dict]:
    """
    Search OpenAlex scholarly graph across publishers (IEEE, arXiv, Springer, Nature, etc.).
    Returns normalized paper metadata.
    """
    params = {
        "search": query,
        "per_page": min(max_results, 20),
        "mailto": "paperpilot.academic@example.com"
    }
    
    try:
        response = requests.get(OPENALEX_WORKS_URL, params=params, timeout=15)
        if response.status_code != 200:
            return []
            
        data = response.json()
        papers = []
        for item in data.get("results", []):
            # Reconstruct abstract from inverted index if present
            abstract = ""
            inverted_index = item.get("abstract_inverted_index")
            if inverted_index:
                words_positions = []
                for word, positions in inverted_index.items():
                    for pos in positions:
                        words_positions.append((pos, word))
                words_positions.sort()
                abstract = " ".join([w for _, w in words_positions])
            else:
                abstract = "No abstract provided in public metadata."

            # Authors
            authorships = item.get("authorships", [])
            authors_list = [a.get("author", {}).get("display_name") for a in authorships if a.get("author", {}).get("display_name")]
            authors_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "") if authors_list else "Unknown Authors"
            
            year = str(item.get("publication_year")) if item.get("publication_year") else "Recent"
            
            # Host / Venue detection
            primary_loc = item.get("primary_location") or {}
            source_info = primary_loc.get("source") or {}
            host_org = source_info.get("host_organization_name", "")
            venue_name = source_info.get("display_name", "")
            
            source_tag = "OpenAlex"
            if "ieee" in host_org.lower() or "ieee" in venue_name.lower():
                source_tag = "IEEE"
            elif "arxiv" in venue_name.lower() or "arxiv" in host_org.lower():
                source_tag = "arXiv"
            elif venue_name:
                source_tag = venue_name[:25]
            elif host_org:
                source_tag = host_org[:25]

            # Direct PDF or DOI URL
            pdf_url = primary_loc.get("pdf_url") or item.get("doi") or primary_loc.get("landing_page_url") or ""
            work_id = item.get("id", "").split("/")[-1]

            papers.append({
                "id": work_id,
                "title": item.get("title", "Untitled").strip(),
                "authors": authors_str,
                "year": year,
                "summary": abstract.strip(),
                "venue": venue_name or host_org or "Academic Venue",
                "source": source_tag,
                "pdf_url": pdf_url,
                "arxiv_id": ""
            })
        return papers
    except Exception:
        return []
