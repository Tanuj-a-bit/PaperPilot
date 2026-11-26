import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini ──
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "models/text-embedding-004"

# ── Chunking ──
CHUNK_SIZE = 500          # words per chunk
CHUNK_OVERLAP = 50        # overlap words

# ── Retrieval ──
TOP_K = 10

# ── External APIs ──
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_API = "http://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"
