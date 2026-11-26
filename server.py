"""FastAPI server for PaperPilot (HTML/CSS/JS frontend).
Serves multi-source academic paper streaming (arXiv, Semantic Scholar, OpenAlex).
Zero local storage, zero vector database persistence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from src.apis.unified_search import search_academic_papers
from src.features.core_features import live_arxiv_qa, live_compare_arxiv, live_research_gaps
from src.features.roadmap import generate_phd_roadmap

app = FastAPI(title="PaperPilot API")

# Serve static files (HTML, CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# ── API Models ──
class SearchRequest(BaseModel):
    topic: str
    source: str = "all"  # 'all', 'arxiv', 'semanticscholar', 'openalex'
    max_results: int = 7

class RoadmapRequest(BaseModel):
    topic: str
    papers: list[dict]

class QARequest(BaseModel):
    question: str
    topic: str = ""

class CompareRequest(BaseModel):
    papers: list[dict]

class GapsRequest(BaseModel):
    topic: str
    papers: list[dict]

# ── Endpoints ──
@app.post("/api/search")
def search_papers(req: SearchRequest):
    try:
        papers = search_academic_papers(req.topic, source=req.source, max_results=req.max_results)
        return {"papers": papers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/roadmap")
def create_roadmap(req: RoadmapRequest):
    try:
        roadmap = generate_phd_roadmap(req.topic, req.papers)
        return {"roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qa")
def ask_question(req: QARequest):
    try:
        result = live_arxiv_qa(req.question, topic=req.topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare")
def compare(req: CompareRequest):
    try:
        result = live_compare_arxiv(req.papers)
        return {"comparison": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gaps")
def discover_gaps(req: GapsRequest):
    try:
        result = live_research_gaps(req.topic, req.papers)
        return {"gaps": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
