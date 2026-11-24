# PaperPilot ✈️

> **An AI-Powered Academic Research Assistant & PhD Literature Roadmap Engine**
> 
> Designed for undergraduate/postgraduate researchers, PhD scholars, and faculty to rapidly synthesize scientific literature, construct guided evolutionary reading paths, perform evidence-grounded Q&A, and identify novel dissertation gaps.

---

## 🌟 Key Features

1. **🗺️ PhD Literature Roadmap**:
   - Rather than browsing papers haphazardly, PaperPilot organizes search queries into a progressive 4-stage learning path:
     - **Stage 1: Foundations & Prerequisites**
     - **Stage 2: Core Architectures & Methods**
     - **Stage 3: SOTA Advances & Specialized Variants**
     - **Stage 4: Open Frontiers & Thesis Gaps**
   - Includes real-time reading progress tracking.

2. **📡 Live arXiv Streaming (Zero Local Storage)**:
   - Queries preprints directly via the arXiv API.
   - Zero local hard drive footprint and zero vector database persistence.

3. **💬 Evidence-Grounded Q&A**:
   - Answers are synthesized strictly from retrieved paper abstracts.
   - Every factual claim links directly to its source with `[Paper Title, arXiv:ID]`.

4. **⚖️ Multi-Paper Structured Comparison**:
   - Generates side-by-side matrices comparing *Objectives*, *Architectures*, *Evaluation Benchmarks*, *Findings*, and *Limitations*.

5. **💡 Research Gap & Dissertation Discovery**:
   - Cross-analyzes literature bottlenecks to formulate viable research hypotheses.

6. **🎨 Academic "Library at Dusk" UI/UX**:
   - Clean, human-crafted design built with semantic HTML, custom CSS, and vanilla JS.
   - **⠶ 9-Dots App Switcher**: Quick-access launcher across all tools.
   - **⋮ 3-Dots Paper Context Menu**: Single-paper Q&A, BibTeX citation copying, and note clipping.
   - **📝 Research Scratchpad**: Floating side drawer (`Cmd + J`) to record insights without navigating away.

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Tanuj-a-bit/PaperPilot.git
cd PaperPilot
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3. Launch the Application
Run the FastAPI web server:
```bash
python3 -m uvicorn server:app --reload --port 8000
```
Open **`http://localhost:8000`** in your browser.

*(Optional)* Run the Streamlit variant:
```bash
streamlit run app.py
```

---

## 🏗️ Architecture & Tech Stack

| Layer | Component |
|---|---|
| **Frontend** | Vanilla HTML5, CSS3 ("Library at Dusk" palette), JavaScript |
| **Backend** | Python, FastAPI, Uvicorn |
| **Data Source** | arXiv API (on-the-fly streaming) |
| **AI / Reasoning** | Google Gemini 2.5 Flash Lite (`google-generativeai`) with automatic exponential backoff |
| **Parsing** | PyMuPDF (`fitz`), Marked.js |
