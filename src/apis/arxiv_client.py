"""Pure on-the-fly arXiv API search & streaming client.
Zero vector stores, zero local files, zero in-memory collections.
Direct API fetch -> Prompt -> Gemini.
"""

import urllib.parse
import xml.etree.ElementTree as ET
import requests

def query_arxiv_live(query: str, max_results: int = 8) -> list[dict]:
    """
    Directly query arXiv API and return metadata + abstracts.
    Nothing is stored anywhere.
    """
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    encoded_query = urllib.parse.urlencode(params)
    url = f"{base_url}?{encoded_query}"
    
    response = requests.get(url, timeout=20)
    if response.status_code != 200:
        return []
    
    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
        published = entry.find("atom:published", ns).text[:4] if entry.find("atom:published", ns) is not None else "Unknown"
        
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None:
                authors.append(name.text)
                
        # Link to abstract and PDF
        id_elem = entry.find("atom:id", ns)
        paper_id_url = id_elem.text.strip() if id_elem is not None else ""
        arxiv_id = paper_id_url.split("/abs/")[-1] if "/abs/" in paper_id_url else ""
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else paper_id_url
        
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            "year": published,
            "summary": summary,
            "arxiv_url": paper_id_url,
            "pdf_url": pdf_url
        })
    return papers
