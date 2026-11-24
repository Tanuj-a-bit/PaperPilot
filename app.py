"""PaperPilot — Research Literature Assistant.
Pure on-the-fly arXiv API search & streaming.
Zero local storage, zero in-memory vector databases.
Editorial/Academic UI design system.
"""

import streamlit as st
from src.apis.arxiv_client import query_arxiv_live
from src.features.core_features import live_arxiv_qa, live_compare_arxiv, live_research_gaps
from src.features.roadmap import generate_phd_roadmap

st.set_page_config(
    page_title="PaperPilot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design System: Library at Dusk (Editorial & Academic) ──
st.markdown("""
<style>
/* Page Background */
.stApp {
    background-color: #FDFBF7 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1C1917 !important;
    border-right: 1px solid #292524 !important;
}
[data-testid="stSidebar"] * {
    color: #E7E5E4 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background-color: #292524 !important;
    border: 1px solid #44403C !important;
    color: #FDFBF7 !important;
    border-radius: 4px !important;
}

/* Typography & Headings */
h1, h2, h3 {
    font-family: 'Charter', 'Georgia', 'Times New Roman', serif !important;
    color: #1C1917 !important;
    font-weight: 600 !important;
}
h1 { font-size: 28px !important; margin-bottom: 2px !important; }
h2 { font-size: 22px !important; margin-top: 18px !important; }
h3 { font-size: 18px !important; margin-top: 14px !important; }

/* Body text & line height */
p, li, span, .stMarkdown {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #44403C;
    font-size: 15px;
    line-height: 1.65;
}

/* Captions & metadata */
.stCaption, small {
    color: #78716C !important;
    font-size: 13px !important;
}

/* Tabs: text-only, quiet elegance with amber underline */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #E7E5E4 !important;
    background-color: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #78716C !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    background-color: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #1C1917 !important;
    border-bottom: 2px solid #B45309 !important;
    font-weight: 600 !important;
}

/* Primary and secondary buttons */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #B45309 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #92400E !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background-color: transparent !important;
    color: #44403C !important;
    border: 1px solid #D6D3D1 !important;
    border-radius: 4px !important;
}

/* Progress bar (amber-700) */
.stProgress > div > div > div > div {
    background-color: #B45309 !important;
}

/* Expanders */
.streamlit-expanderHeader {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #44403C !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E7E5E4 !important;
    border-radius: 4px !important;
}

/* Dividers */
hr {
    border: none !important;
    border-top: 1px solid #E7E5E4 !important;
    margin: 18px 0 !important;
}

/* Alerts and notifications */
.stAlert[data-baseweb="notification"] {
    border-radius: 4px !important;
    border: 1px solid #E7E5E4 !important;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
}
th {
    background: #1C1917 !important;
    color: #FDFBF7 !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    text-align: left;
    font-size: 13px !important;
}
td {
    padding: 10px 14px !important;
    border-bottom: 1px solid #E7E5E4 !important;
    font-size: 14px !important;
    color: #44403C !important;
}
tr:hover td {
    background-color: #F5F5F4 !important;
}

/* Links */
a {
    color: #1D4ED8 !important;
    text-decoration: none !important;
}
a:hover {
    color: #1E40AF !important;
    text-decoration: underline !important;
}

/* Flattened chat/message area */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 6px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ──
if "live_papers" not in st.session_state:
    st.session_state.live_papers = []
if "roadmap_result" not in st.session_state:
    st.session_state.roadmap_result = None
if "read_papers" not in st.session_state:
    st.session_state.read_papers = set()
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# ── Sidebar ──
with st.sidebar:
    st.markdown("### PaperPilot")
    st.caption("Research Literature Assistant · Live arXiv Stream")
    st.divider()
    
    st.markdown("**Search arXiv**")
    topic = st.text_input("Topic or sub-field", value="Retrieval Augmented Generation")
    max_papers = st.slider("Number of papers", min_value=3, max_value=15, value=7)
    
    if st.button("Fetch Papers", use_container_width=True, type="primary"):
        with st.spinner(f"Querying arXiv for recent work on {topic}..."):
            papers = query_arxiv_live(topic, max_results=max_papers)
            st.session_state.live_papers = papers
            st.session_state.roadmap_result = None
            if papers:
                st.success(f"Retrieved {len(papers)} papers")
            else:
                st.warning("No papers found. Try broadening the search query.")

    st.divider()
    paper_count = len(st.session_state.live_papers)
    st.write(f"**{paper_count}** papers currently active")
    
    if st.button("Reset Session", use_container_width=True):
        st.session_state.live_papers = []
        st.session_state.roadmap_result = None
        st.session_state.qa_history = []
        st.session_state.read_papers = set()
        st.rerun()

# ── Main Header ──
st.title("PaperPilot")
st.caption("Research literature assistant — live arXiv search, guided PhD roadmaps, citation-grounded Q&A")

# ── Tabs ──
tab_roadmap, tab_feed, tab_qa, tab_compare, tab_gaps = st.tabs([
    "Roadmap", "Papers", "Ask", "Compare", "Gaps"
])

# ── TAB 1: PhD Research Roadmap ──
with tab_roadmap:
    st.subheader("PhD Research Roadmap")
    st.write(
        "A structured curriculum designed for doctoral scholars to navigate a subfield progressively: "
        "prerequisites, foundational models, modern optimizations, and open thesis opportunities."
    )
    
    if not st.session_state.live_papers:
        st.info("Enter a research topic in the sidebar and fetch papers to generate a roadmap.")
    else:
        col_btn, col_progress = st.columns([1, 2])
        with col_btn:
            if st.button("Generate Roadmap", type="primary", use_container_width=True):
                with st.spinner("Mapping literature progression with Gemini..."):
                    roadmap = generate_phd_roadmap(topic, st.session_state.live_papers)
                    st.session_state.roadmap_result = roadmap
        
        if st.session_state.roadmap_result:
            roadmap = st.session_state.roadmap_result
            total_papers = sum(len(s.get("papers", [])) for s in roadmap.get("stages", []))
            read_count = len(st.session_state.read_papers)
            progress = (read_count / total_papers) if total_papers > 0 else 0.0
            
            with col_progress:
                st.write(f"Reading Progress: **{read_count} of {total_papers}** papers completed")
                st.progress(min(progress, 1.0))
                
            if roadmap.get("executive_summary"):
                st.info(roadmap.get("executive_summary"))
            
            stage_colors = {
                1: "#78716C",  # stone
                2: "#1D4ED8",  # blue
                3: "#B45309",  # amber
                4: "#B91C1C",  # red
            }
            
            for stage in roadmap.get("stages", []):
                s_num = stage.get("stage_number", 1)
                border_color = stage_colors.get(s_num, "#78716C")
                
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding-left: 14px; margin-top: 24px; margin-bottom: 12px;">
                    <div style="font-family: 'Charter', serif; font-size: 19px; font-weight: 600; color: #1C1917;">
                        {stage.get('stage_name', f'Stage {s_num}')}
                    </div>
                    <div style="font-size: 13px; color: #78716C; margin-top: 2px;">
                        Objective: {stage.get('stage_goal', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Papers
                for paper in stage.get("papers", []):
                    title = paper.get("title", "")
                    is_read = title in st.session_state.read_papers
                    
                    chk = st.checkbox(f"{title} ({paper.get('year', '')})", value=is_read, key=f"rd_chk_{title}")
                    if chk:
                        st.session_state.read_papers.add(title)
                    else:
                        st.session_state.read_papers.discard(title)
                        
                    if paper.get("why_read"):
                        st.caption(f"**Rationale:** {paper.get('why_read')}")
                    if paper.get("key_takeaway"):
                        st.caption(f"**Key Takeaway:** {paper.get('key_takeaway')}")
                    st.divider()
                
                # Gaps
                if "research_gaps" in stage and stage["research_gaps"]:
                    for gap in stage.get("research_gaps", []):
                        st.markdown(f"""
                        <div style="background-color: #FFFBEB; border-left: 3px solid #B91C1C; padding: 12px 16px; margin: 10px 0; border-radius: 4px;">
                            <div style="font-weight: 600; font-size: 14px; color: #1C1917;">{gap.get('gap_title')}</div>
                            <div style="font-size: 13px; color: #44403C; margin-top: 4px;"><b>Limitation:</b> {gap.get('problem_statement')}</div>
                            <div style="font-size: 13px; color: #92400E; margin-top: 3px;"><b>PhD Direction:</b> {gap.get('suggested_approach')}</div>
                        </div>
                        """, unsafe_allow_html=True)

# ── TAB 2: Papers ──
with tab_feed:
    st.subheader("Active arXiv Papers")
    st.caption("Live abstracts streamed directly from the arXiv API.")
    
    if not st.session_state.live_papers:
        st.info("No papers loaded. Use the sidebar to fetch papers for your topic.")
    else:
        for idx, p in enumerate(st.session_state.live_papers):
            st.markdown(f"**{idx+1}. {p['title']}** ({p['year']})")
            st.caption(f"{p['authors']} · arXiv: `{p['arxiv_id']}`")
            
            c1, c2 = st.columns([5, 1])
            with c1:
                with st.expander("Abstract"):
                    st.write(p["summary"])
            with c2:
                if p.get("pdf_url"):
                    st.link_button("PDF →", p["pdf_url"], use_container_width=True)
            st.divider()

# ── TAB 3: Q&A ──
with tab_qa:
    st.subheader("Citation-Grounded Q&A")
    st.caption("Ask technical questions across the literature. Answers cite specific papers and arXiv identifiers.")
    
    user_q = st.text_input("Question", placeholder="e.g. What techniques are used to mitigate retrieval latency in multi-hop QA?")
    
    if st.button("Ask", type="primary"):
        if user_q.strip():
            with st.spinner("Retrieving relevant literature and synthesizing response..."):
                res = live_arxiv_qa(user_q, topic=topic)
                st.session_state.qa_history.append((user_q, res))
                
    for q, ans in reversed(st.session_state.qa_history):
        st.markdown(f"**Q:** {q}")
        st.markdown(ans["answer"])
        if ans.get("papers"):
            with st.expander("Sources"):
                for p in ans["papers"]:
                    st.caption(f"— {p['title']} ({p['year']}) [arXiv:{p['arxiv_id']}]({p['pdf_url']})")
        st.divider()

# ── TAB 4: Compare ──
with tab_compare:
    st.subheader("Multi-Paper Comparison")
    st.caption("Select two or more papers to generate a structured comparative analysis.")
    
    if len(st.session_state.live_papers) < 2:
        st.info("Fetch at least two papers from arXiv via the sidebar to run a comparison.")
    else:
        titles = [f"{p['title']} ({p['year']})" for p in st.session_state.live_papers]
        selected = st.multiselect("Select papers:", titles, default=titles[:2])
        
        if st.button("Compare Selected", type="primary"):
            if len(selected) < 2:
                st.error("Select at least two papers.")
            else:
                chosen_data = [p for p in st.session_state.live_papers if f"{p['title']} ({p['year']})" in selected]
                with st.spinner("Comparing across objectives, methods, benchmarks, and limitations..."):
                    res = live_compare_arxiv(chosen_data)
                    st.markdown(res)

# ── TAB 5: Gaps ──
with tab_gaps:
    st.subheader("Research Gaps & Dissertation Ideas")
    st.caption("Synthesize recurring limitations and methodological blind spots across papers to discover novel research angles.")
    
    if not st.session_state.live_papers:
        st.info("Fetch papers in the sidebar to analyze research gaps.")
    else:
        if st.button("Uncover Research Gaps", type="primary"):
            with st.spinner("Analyzing limitations and synthesizing candidate thesis problems..."):
                gaps = live_research_gaps(topic, st.session_state.live_papers)
                st.markdown(gaps)
