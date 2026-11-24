"""Extract and chunk text from in-memory PDF bytes (never saved to disk)."""

import fitz  # PyMuPDF
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf_bytes(pdf_bytes: bytes, paper_title: str = "Unknown") -> list[dict]:
    """
    Extracts text page-by-page from raw in-memory PDF bytes.
    Returns list of page dicts: [{'page_num': 1, 'text': '...'}]
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "page_num": page_idx + 1,
                "text": text,
                "paper_title": paper_title
            })
    doc.close()
    return pages


def chunk_extracted_pages(pages: list[dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Splits text across pages into overlapping chunks while preserving paper title and page citations.
    """
    chunks = []
    chunk_id = 0
    
    for page in pages:
        words = page["text"].split()
        if not words:
            continue
        
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "chunk_id": f"{page['paper_title']}_p{page['page_num']}_{chunk_id}",
                "text": chunk_text,
                "paper_title": page["paper_title"],
                "page_num": page["page_num"]
            })
            chunk_id += 1
            if end == len(words):
                break
            start += (chunk_size - overlap)
            
    return chunks
