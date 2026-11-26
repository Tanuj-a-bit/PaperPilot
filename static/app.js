// PaperPilot — Frontend logic supporting Multi-Source Literature (IEEE, Semantic Scholar, OpenAlex, arXiv)

let activePapers = [];
let roadmapData = null;
let readPaperTitles = new Set();

// ── DOM References ──
const globalTopicInput = document.getElementById('globalTopicInput');
const sourceSelect = document.getElementById('sourceSelect');
const topbarFetchBtn = document.getElementById('topbarFetchBtn');
const fetchCountSlider = document.getElementById('fetchCountSlider');
const fetchCountVal = document.getElementById('fetchCountVal');
const paperTabCount = document.getElementById('paperTabCount');

const nineDotsBtn = document.getElementById('nineDotsBtn');
const nineDotsMenu = document.getElementById('nineDotsMenu');
const notesDrawer = document.getElementById('notesDrawer');
const scratchpadArea = document.getElementById('scratchpadArea');

const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');
const spinnerOverlay = document.getElementById('spinnerOverlay');
const spinnerText = document.getElementById('spinnerText');
const toast = document.getElementById('toast');

// ── Toast Notification Helper ──
function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 2500);
}

// ── 9-Dots Menu Toggle ──
nineDotsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    nineDotsMenu.classList.toggle('hidden');
});

// Close open dropdowns on body click
document.addEventListener('click', (e) => {
    if (!nineDotsMenu.contains(e.target) && e.target !== nineDotsBtn) {
        nineDotsMenu.classList.add('hidden');
    }
    // Close 3-dots menus
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (!menu.contains(e.target) && !menu.previousElementSibling.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });
});

// Bento item navigation
document.querySelectorAll('.bento-item').forEach(item => {
    item.addEventListener('click', () => {
        const targetTab = item.getAttribute('data-target');
        if (targetTab) {
            switchTab(targetTab);
            nineDotsMenu.classList.add('hidden');
        }
    });
});

// ── Scratchpad / Notes Drawer ──
function toggleScratchpad() {
    notesDrawer.classList.toggle('hidden');
}
window.toggleScratchpad = toggleScratchpad;
document.getElementById('toggleNotesBtn').addEventListener('click', toggleScratchpad);

// Keyboard shortcuts (Cmd+J or Ctrl+J to toggle notes)
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'j') {
        e.preventDefault();
        toggleScratchpad();
    }
    if (e.key === 'Escape') {
        nineDotsMenu.classList.add('hidden');
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.add('hidden'));
    }
});

document.getElementById('copyNotesBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(scratchpadArea.value);
    showToast('Notes copied to clipboard!');
});
document.getElementById('clearNotesBtn').addEventListener('click', () => {
    if (confirm('Clear scratchpad?')) {
        scratchpadArea.value = '';
    }
});

// ── Slider Sync ──
fetchCountSlider.addEventListener('input', (e) => {
    fetchCountVal.textContent = e.target.value;
});

// ── Tabs Switching ──
function switchTab(tabId) {
    tabBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-tab') === tabId));
    tabPanes.forEach(p => p.classList.toggle('active', p.id === `tab-${tabId}`));
}

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        switchTab(btn.getAttribute('data-tab'));
    });
});

// ── Spinner Helpers ──
function showSpinner(text) {
    spinnerText.textContent = text;
    spinnerOverlay.classList.remove('hidden');
}
function hideSpinner() {
    spinnerOverlay.classList.add('hidden');
}

// ── 1. Fetch Papers across Selected Source(s) ──
topbarFetchBtn.addEventListener('click', async () => {
    const topic = globalTopicInput.value.trim();
    if (!topic) return alert('Please enter a research topic.');

    const source = sourceSelect.value;
    const sourceLabel = sourceSelect.options[sourceSelect.selectedIndex].text;

    showSpinner(`Querying ${sourceLabel} for "${topic}"...`);
    try {
        const res = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic,
                source,
                max_results: parseInt(fetchCountSlider.value)
            })
        });
        const data = await res.json();
        activePapers = data.papers || [];
        paperTabCount.textContent = activePapers.length;
        roadmapData = null;
        readPaperTitles.clear();

        renderPapersList();
        renderCompareSelector();
        document.getElementById('roadmapContent').innerHTML = '<p class="placeholder-text">Click "Generate Roadmap" to synthesize a curriculum from fetched papers.</p>';
        document.getElementById('roadmapProgressWrap').classList.add('hidden');

        showToast(`Retrieved ${activePapers.length} papers from ${sourceLabel}!`);
        switchTab('papers');
    } catch (err) {
        alert('Failed to fetch literature: ' + err.message);
    } finally {
        hideSpinner();
    }
});

// ── 2. Render Papers List with Source Badges & 3-Dots Menu (⋮) ──
function renderPapersList() {
    const container = document.getElementById('papersList');
    if (!activePapers.length) {
        container.innerHTML = '<p class="placeholder-text">No papers found for this query.</p>';
        return;
    }

    container.innerHTML = activePapers.map((p, idx) => {
        // Source Badge class
        let badgeClass = 'badge-other';
        const srcLower = (p.source || '').toLowerCase();
        if (srcLower.includes('ieee')) badgeClass = 'badge-ieee';
        else if (srcLower.includes('arxiv')) badgeClass = 'badge-arxiv';

        const sourceBadge = `<span class="badge-source ${badgeClass}">${p.source || 'Scholar'}</span>`;

        return `
        <div class="paper-card">
            <div class="paper-card-header">
                <div class="paper-title">${idx + 1}. ${p.title} (${p.year})</div>
                
                <!-- 3-Dots Action Menu -->
                <div class="menu-wrap">
                    <button class="three-dots-btn" onclick="togglePaperMenu(event, 'p-menu-${idx}')">⋮</button>
                    <div id="p-menu-${idx}" class="dropdown-menu hidden">
                        <button onclick="askSinglePaper(${idx})">💬 Ask about this paper</button>
                        <button onclick="addPaperToCompare(${idx})">⚖️ Add to Comparison</button>
                        <button onclick="copyBibtex(${idx})">📋 Copy BibTeX Citation</button>
                        <button onclick="clipToScratchpad(${idx})">📌 Clip to Scratchpad</button>
                    </div>
                </div>
            </div>

            <div class="paper-meta">
                ${sourceBadge}
                ${p.authors} · <em>${p.venue || 'Academic Publication'}</em>
            </div>
            
            <div class="paper-links">
                <button class="btn btn-secondary btn-sm" onclick="toggleAbstract(${idx})">Toggle Abstract</button>
                ${p.pdf_url ? `<a href="${p.pdf_url}" target="_blank" rel="noopener">Open Paper / PDF →</a>` : ''}
            </div>
            <div id="abs-${idx}" class="paper-abstract hidden">${p.summary}</div>
        </div>
        `;
    }).join('');
}

window.toggleAbstract = function(idx) {
    const el = document.getElementById(`abs-${idx}`);
    el.classList.toggle('hidden');
};

// ── 3-Dots Menu Functions ──
window.togglePaperMenu = function(e, menuId) {
    e.stopPropagation();
    const menu = document.getElementById(menuId);
    const wasHidden = menu.classList.contains('hidden');
    // Hide all other menus first
    document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.add('hidden'));
    if (wasHidden) menu.classList.remove('hidden');
};

window.askSinglePaper = function(idx) {
    const p = activePapers[idx];
    document.getElementById('questionInput').value = `Regarding "${p.title}": `;
    switchTab('ask');
    document.getElementById('questionInput').focus();
};

window.addPaperToCompare = function(idx) {
    switchTab('compare');
    const chk = document.querySelector(`.compare-chk[value="${idx}"]`);
    if (chk) chk.checked = true;
    showToast(`Added "${activePapers[idx].title.slice(0, 30)}..." to Compare`);
};

window.copyBibtex = function(idx) {
    const p = activePapers[idx];
    const key = (p.authors.split(' ')[0] || 'paper') + p.year;
    const bibtex = `@article{${key.toLowerCase()},\n  title={${p.title}},\n  author={${p.authors}},\n  year={${p.year}},\n  venue={${p.venue || 'IEEE/arXiv'}},\n  url={${p.pdf_url || ''}}\n}`;
    navigator.clipboard.writeText(bibtex);
    showToast('BibTeX citation copied to clipboard!');
};

window.clipToScratchpad = function(idx) {
    const p = activePapers[idx];
    notesDrawer.classList.remove('hidden');
    const clip = `\n[Paper Citation] ${p.title} (${p.year})\nAuthors: ${p.authors} [${p.source} - ${p.venue || ''}]\nNotes: \n`;
    scratchpadArea.value += clip;
    showToast('Clipped to scratchpad!');
};

// ── 3. PhD Roadmap Generation ──
document.getElementById('genRoadmapBtn').addEventListener('click', async () => {
    if (!activePapers.length) return alert('Please fetch papers first using the search bar.');

    const topic = globalTopicInput.value.trim();
    showSpinner('Synthesizing PhD curriculum & literature evolution across papers via Gemini...');
    try {
        const res = await fetch('/api/roadmap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, papers: activePapers })
        });
        const data = await res.json();
        roadmapData = data.roadmap || {};
        renderRoadmap();
        showToast('Roadmap generated!');
    } catch (err) {
        alert('Failed to generate roadmap: ' + err.message);
    } finally {
        hideSpinner();
    }
});

function renderRoadmap() {
    const container = document.getElementById('roadmapContent');
    const progressWrap = document.getElementById('roadmapProgressWrap');
    if (!roadmapData || !roadmapData.stages) {
        container.innerHTML = '<p class="placeholder-text">Unable to construct roadmap.</p>';
        return;
    }

    progressWrap.classList.remove('hidden');
    updateRoadmapProgress();

    let html = '';
    if (roadmapData.executive_summary) {
        html += `<p style="font-size: 14px; color: var(--text-body); margin-bottom: 20px; font-style: italic;">${roadmapData.executive_summary}</p>`;
    }

    roadmapData.stages.forEach(stage => {
        const sNum = stage.stage_number || 1;
        html += `
            <div class="stage-block s${sNum}">
                <div class="stage-title">${stage.stage_name || 'Stage ' + sNum}</div>
                <div class="stage-goal">Objective: ${stage.stage_goal || ''}</div>
        `;

        if (stage.papers && stage.papers.length) {
            stage.papers.forEach(p => {
                const isChecked = readPaperTitles.has(p.title);
                html += `
                    <div class="stage-item">
                        <label>
                            <input type="checkbox" onchange="toggleRead('${encodeURIComponent(p.title)}', this)" ${isChecked ? 'checked' : ''}>
                            <span>${p.title} (${p.year || ''})</span>
                        </label>
                        ${p.why_read ? `<div class="takeaway"><strong>Why read:</strong> ${p.why_read}</div>` : ''}
                        ${p.key_takeaway ? `<div class="takeaway"><strong>Key Takeaway:</strong> ${p.key_takeaway}</div>` : ''}
                    </div>
                `;
            });
        }

        if (stage.research_gaps && stage.research_gaps.length) {
            stage.research_gaps.forEach(g => {
                html += `
                    <div class="gap-card">
                        <h4>${g.gap_title}</h4>
                        <div class="gap-desc"><b>Limitation:</b> ${g.problem_statement}</div>
                        <div class="gap-sol"><b>PhD Direction:</b> ${g.suggested_approach}</div>
                    </div>
                `;
            });
        }

        html += `</div>`;
    });

    container.innerHTML = html;
}

window.toggleRead = function(encodedTitle, checkbox) {
    const title = decodeURIComponent(encodedTitle);
    if (checkbox.checked) {
        readPaperTitles.add(title);
    } else {
        readPaperTitles.delete(title);
    }
    updateRoadmapProgress();
};

function updateRoadmapProgress() {
    if (!roadmapData || !roadmapData.stages) return;
    let total = 0;
    roadmapData.stages.forEach(s => {
        if (s.papers) total += s.papers.length;
    });
    const read = readPaperTitles.size;
    const pct = total > 0 ? Math.round((read / total) * 100) : 0;

    document.getElementById('progressText').textContent = `${read} of ${total}`;
    document.getElementById('progressPct').textContent = `${pct}%`;
    document.getElementById('progressBar').style.width = `${pct}%`;
}

// ── 4. Citation-Grounded Q&A ──
document.getElementById('askBtn').addEventListener('click', async () => {
    const question = document.getElementById('questionInput').value.trim();
    if (!question) return;

    const topic = globalTopicInput.value.trim();
    showSpinner('Retrieving multi-source literature and reasoning with Gemini...');
    try {
        const res = await fetch('/api/qa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, topic })
        });
        const data = await res.json();
        
        const qaContainer = document.getElementById('qaResults');
        const card = document.createElement('div');
        card.className = 'qa-card';
        card.innerHTML = `
            <div class="qa-q">Q: ${question}</div>
            <div class="qa-a">${marked.parse(data.answer || '')}</div>
        `;
        qaContainer.prepend(card);
        document.getElementById('questionInput').value = '';
    } catch (err) {
        alert('Q&A failed: ' + err.message);
    } finally {
        hideSpinner();
    }
});

// ── 5. Comparison ──
function renderCompareSelector() {
    const wrap = document.getElementById('compareSelectWrap');
    if (!activePapers.length) {
        wrap.innerHTML = '<p class="placeholder-text">Fetch papers first to select items for comparison.</p>';
        return;
    }

    wrap.innerHTML = activePapers.map((p, idx) => `
        <label style="display: block; margin: 6px 0; font-size: 14px;">
            <input type="checkbox" class="compare-chk" value="${idx}" ${idx < 2 ? 'checked' : ''}>
            [${p.source}] ${p.title} (${p.year})
        </label>
    `).join('');
}

document.getElementById('compareBtn').addEventListener('click', async () => {
    const checkedBoxes = document.querySelectorAll('.compare-chk:checked');
    if (checkedBoxes.length < 2) return alert('Select at least 2 papers to compare.');

    const selectedPapers = Array.from(checkedBoxes).map(cb => activePapers[parseInt(cb.value)]);
    showSpinner('Synthesizing comparative matrix across papers with Gemini...');
    try {
        const res = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ papers: selectedPapers })
        });
        const data = await res.json();
        document.getElementById('compareResult').innerHTML = marked.parse(data.comparison || '');
    } catch (err) {
        alert('Comparison failed: ' + err.message);
    } finally {
        hideSpinner();
    }
});

// ── 6. Gaps Discovery ──
document.getElementById('gapsBtn').addEventListener('click', async () => {
    if (!activePapers.length) return alert('Please fetch papers first.');

    const topic = globalTopicInput.value.trim();
    showSpinner('Analyzing limitations and finding thesis gaps with Gemini...');
    try {
        const res = await fetch('/api/gaps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, papers: activePapers })
        });
        const data = await res.json();
        document.getElementById('gapsResult').innerHTML = marked.parse(data.gaps || '');
    } catch (err) {
        alert('Gaps discovery failed: ' + err.message);
    } finally {
        hideSpinner();
    }
});
