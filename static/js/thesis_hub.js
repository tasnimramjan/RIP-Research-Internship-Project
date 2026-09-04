// ==========================================================
// Client-side Controller for 5 Research & Academic Features
// (Progress Tracker & AI, LaTeX Editor, Citations, Resources, Archive)
// ==========================================================

const ThesisHub = {
  currentDocId: 1,
  currentCitations: [],

  init() {
    this.setupModals();
    this.setupTracker();
    this.setupOverleaf();
    this.setupCitations();
    this.setupResources();
    this.setupArchive();

    // Initial load
    this.loadMilestones();
    this.loadDocument();
    this.loadCitations();
    this.loadResources();
    this.loadArchive();
  },

  // ── Modal Handlers ─────────────────────────────────────
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('open');
      modal.style.display = 'flex';

      if (modalId === 'gemini-key-modal') {
        const keyInput = document.getElementById('gemini-key-input');
        if (keyInput) keyInput.value = localStorage.getItem('gemini_api_key') || '';
      }
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('open');
      modal.classList.add('hidden');
      modal.style.display = 'none';
    }
  },

  setupModals() {
    const wire = (openBtnId, closeBtnId, modalId) => {
      const openBtn = document.getElementById(openBtnId);
      const closeBtn = document.getElementById(closeBtnId);
      const modal = document.getElementById(modalId);

      if (openBtn) {
        openBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.openModal(modalId);
        });
      }

      if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.closeModal(modalId);
        });
      }

      // Close when clicking overlay backdrop
      if (modal) {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            this.closeModal(modalId);
          }
        });
      }
    };

    wire('open-milestone-modal-btn', 'close-milestone-modal-btn', 'milestone-modal');
    wire('edit-feedback-btn', 'close-supervisor-modal-btn', 'supervisor-modal');
    wire('open-citation-modal-btn', 'close-citation-modal-btn', 'citation-modal');
    wire('open-resource-modal-btn', 'close-resource-modal-btn', 'resource-modal');
    wire('open-archive-modal-btn', 'close-archive-modal-btn', 'archive-modal');
    wire('open-gemini-key-btn', 'close-gemini-key-btn', 'gemini-key-modal');
  },

  // ── FEATURE 11: Milestones & Gemini AI Assistant ───────
  setupTracker() {
    const addForm = document.getElementById('add-milestone-form');
    if (addForm) {
      addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          title: document.getElementById('ms-title').value,
          phase: document.getElementById('ms-phase').value,
          due_date: document.getElementById('ms-date').value,
          progress: 0,
          status: 'Pending'
        };

        try {
          const res = await fetch('/api/milestones/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            this.closeModal('milestone-modal');
            addForm.reset();
            this.loadMilestones();
          }
        } catch (err) {
          console.error("Error adding milestone:", err);
        }
      });
    }

    const aiBtn = document.getElementById('ai-submit-btn');
    const aiPrompt = document.getElementById('ai-input-prompt');
    const chatHistory = document.getElementById('ai-chat-history');

    if (aiBtn && aiPrompt && chatHistory) {
      const sendPrompt = async () => {
        const text = aiPrompt.value.trim();
        if (!text) return;

        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.textContent = text;
        chatHistory.appendChild(userMsg);

        aiPrompt.value = '';
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
          const apiKey = localStorage.getItem('gemini_api_key') || '';
          const res = await fetch('/api/ai-assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text, context: '', api_key: apiKey })
          });
          const data = await res.json();

          const aiMsg = document.createElement('div');
          aiMsg.className = 'chat-message ai';
          aiMsg.innerText = data.response || "No response received.";
          chatHistory.appendChild(aiMsg);
          chatHistory.scrollTop = chatHistory.scrollHeight;
        } catch (err) {
          console.error("Error calling AI assistant:", err);
        }
      };

      aiBtn.addEventListener('click', sendPrompt);
      aiPrompt.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendPrompt();
        }
      });
    }

    const keyForm = document.getElementById('gemini-key-form');
    if (keyForm) {
      keyForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const key = document.getElementById('gemini-key-input')?.value.trim() || '';
        if (key) {
          localStorage.setItem('gemini_api_key', key);
          alert('Gemini API Key saved successfully in browser storage!');
        } else {
          localStorage.removeItem('gemini_api_key');
          alert('Gemini API Key cleared.');
        }
        this.closeModal('gemini-key-modal');
      });
    }

    const clearKeyBtn = document.getElementById('clear-gemini-key-btn');
    if (clearKeyBtn) {
      clearKeyBtn.addEventListener('click', () => {
        localStorage.removeItem('gemini_api_key');
        const keyInput = document.getElementById('gemini-key-input');
        if (keyInput) keyInput.value = '';
        alert('Gemini API Key cleared.');
        this.closeModal('gemini-key-modal');
      });
    }
  },

  async loadMilestones() {
    try {
      const res = await fetch('/api/milestones');
      const data = await res.json();
      const container = document.getElementById('milestones-list');
      if (!container || !Array.isArray(data)) return;

      container.innerHTML = '';
      let totalProgress = 0;

      data.forEach(item => {
        totalProgress += item.progress;
        const card = document.createElement('div');
        card.className = 'milestone-card';
        card.innerHTML = `
          <div class="milestone-header">
            <span>${item.title} <small style="color:var(--text-muted);">(${item.phase})</small></span>
            <span class="badge ${item.status === 'Completed' ? 'badge-success' : (item.status === 'In Progress' ? 'badge-warning' : 'badge-info')}">${item.status}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${item.progress}%"></div>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
            <small style="color:var(--text-muted)">Progress: ${item.progress}% | Due: ${item.due_date || 'N/A'}</small>
            <div class="milestone-actions">
              <button class="btn btn-sm btn-outline prog-btn" data-id="${item.id}" data-prog="${Math.max(0, item.progress - 25)}">-25%</button>
              <button class="btn btn-sm btn-outline prog-btn" data-id="${item.id}" data-prog="${Math.min(100, item.progress + 25)}">+25%</button>
            </div>
          </div>
        `;
        container.appendChild(card);
      });

      const averageProgress = data.length ? Math.round(totalProgress / data.length) : 0;
      const overallEl = document.getElementById('overall-percentage');
      if (overallEl) overallEl.textContent = `${averageProgress}%`;

      container.querySelectorAll('.prog-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const id = e.target.getAttribute('data-id');
          const newProg = parseInt(e.target.getAttribute('data-prog'));
          const newStatus = newProg >= 100 ? 'Completed' : (newProg > 0 ? 'In Progress' : 'Pending');

          await fetch('/api/milestones/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, progress: newProg, status: newStatus })
          });
          ThesisHub.loadMilestones();
        });
      });
    } catch (err) {
      console.error("Error loading milestones:", err);
    }
  },

  // ── FEATURE 12: Overleaf Editor & Supervisor Approval ─
  setupOverleaf() {
    const latexInput = document.getElementById('latex-input');
    if (latexInput) {
      latexInput.addEventListener('input', (e) => this.renderLatexPreview(e.target.value));
    }

    const saveBtn = document.getElementById('save-doc-btn');
    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        const content = latexInput ? latexInput.value : '';
        await fetch('/api/documents/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: this.currentDocId, content, version: 'v1.3' })
        });
        alert('LaTeX Document saved successfully!');
      });
    }

    const supForm = document.getElementById('supervisor-form');
    if (supForm) {
      supForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const status = document.getElementById('sup-status-select').value;
        const feedback = document.getElementById('sup-feedback-input').value;

        await fetch('/api/documents/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: this.currentDocId, status, feedback })
        });

        this.updateSupervisorUI(status, feedback);
        this.closeModal('supervisor-modal');
      });
    }

    const aiEnhanceBtn = document.getElementById('ai-suggest-editor-btn');
    if (aiEnhanceBtn && latexInput) {
      aiEnhanceBtn.addEventListener('click', async () => {
        const text = latexInput.value;
        const apiKey = localStorage.getItem('gemini_api_key') || '';
        const res = await fetch('/api/ai-assistant', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: 'improve and polish LaTeX content', context: text.slice(0, 300), api_key: apiKey })
        });
        const data = await res.json();
        alert(data.response || 'AI enhancement complete.');
      });
    }
  },

  async loadDocument() {
    try {
      const res = await fetch('/api/documents');
      const docs = await res.json();
      if (docs && docs.length > 0) {
        const doc = docs[0];
        this.currentDocId = doc.id;
        const latexInput = document.getElementById('latex-input');
        if (latexInput) latexInput.value = doc.content;

        const verBadge = document.getElementById('doc-version-badge');
        if (verBadge) verBadge.textContent = doc.version || 'v1.0';

        this.updateSupervisorUI(doc.status, doc.supervisor_feedback);
        this.renderLatexPreview(doc.content);
      }
    } catch (err) {
      console.error("Error loading document:", err);
    }
  },

  updateSupervisorUI(status, feedback) {
    const statusBadge = document.getElementById('supervisor-status-badge');
    const feedbackText = document.getElementById('supervisor-feedback-text');

    if (statusBadge && feedbackText) {
      statusBadge.textContent = status || 'Draft';
      feedbackText.textContent = feedback || 'No comments provided.';

      statusBadge.className = 'badge ';
      if (status === 'Approved') statusBadge.classList.add('badge-success');
      else if (status === 'Needs Revision') statusBadge.classList.add('badge-warning');
      else if (status === 'Rejected') statusBadge.classList.add('badge-danger');
      else statusBadge.classList.add('badge-info');
    }

    const sel = document.getElementById('sup-status-select');
    const inp = document.getElementById('sup-feedback-input');
    if (sel) sel.value = status || 'Under Review';
    if (inp) inp.value = feedback || '';
  },

  renderLatexPreview(code) {
    const latexPreview = document.getElementById('latex-preview');
    if (!latexPreview || !code) return;

    let html = code
      .replace(/\\documentclass\{.*?\}/g, '')
      .replace(/\\title\{(.*?)\}/g, '<h1>$1</h1>')
      .replace(/\\author\{(.*?)\}/g, '<p style="text-align:center; color:#475569;"><strong>Author:</strong> $1</p>')
      .replace(/\\date\{(.*?)\}/g, '<p style="text-align:center; color:#94a3b8; font-size:0.9rem;">$1</p>')
      .replace(/\\begin\{document\}/g, '')
      .replace(/\\end\{document\}/g, '')
      .replace(/\\maketitle/g, '<hr style="margin:16px 0; border:0; border-top:1px solid #e2e8f0;">')
      .replace(/\\section\{(.*?)\}/g, '<h2>$1</h2>')
      .replace(/\\subsection\{(.*?)\}/g, '<h3>$1</h3>')
      .replace(/\\textbf\{(.*?)\}/g, '<strong>$1</strong>')
      .replace(/\\textit\{(.*?)\}/g, '<em>$1</em>')
      .replace(/\n\n/g, '<p></p>');

    latexPreview.innerHTML = html;
  },

  // ── FEATURE 13: Citations & Reference Manager ──────────
  setupCitations() {
    const styleEl = document.getElementById('citation-style');
    if (styleEl) styleEl.addEventListener('change', () => this.renderCitations());

    const addCitForm = document.getElementById('add-citation-form');
    if (addCitForm) {
      addCitForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          title: document.getElementById('cit-title').value,
          authors: document.getElementById('cit-authors').value,
          year: parseInt(document.getElementById('cit-year').value || '2026'),
          journal: document.getElementById('cit-journal').value,
          doi: document.getElementById('cit-doi').value,
          citation_type: document.getElementById('cit-type').value
        };

        await fetch('/api/citations/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        this.closeModal('citation-modal');
        addCitForm.reset();
        this.loadCitations();
      });
    }
  },

  formatCitationText(c, style, isHtml = false) {
    const emStart = isHtml ? '<em>' : '';
    const emEnd = isHtml ? '</em>' : '';
    const journal = c.journal || '';
    const doi = c.doi || 'N/A';

    if (style === 'APA') {
      return `${c.authors} (${c.year}). ${c.title}. ${emStart}${journal}${emEnd}. DOI: ${doi}`;
    } else if (style === 'IEEE') {
      return `${c.authors}, "${c.title}," ${emStart}${journal}${emEnd}, ${c.year}.`;
    } else if (style === 'MLA') {
      return `${c.authors}. "${c.title}." ${emStart}${journal}${emEnd}, ${c.year}.`;
    } else if (style === 'BibTeX') {
      const citeKey = `ref_${c.id || c.title.toLowerCase().replace(/[^a-z0-9]/g, '_').slice(0, 15)}`;
      return `@article{${citeKey},\n  author = {${c.authors}},\n  title = {${c.title}},\n  journal = {${journal}},\n  year = {${c.year}},\n  doi = {${doi}}\n}`;
    }
    return `${c.authors}. ${c.title} (${c.year}).`;
  },

  async loadCitations() {
    try {
      const res = await fetch('/api/citations');
      this.currentCitations = await res.json();
      this.renderCitations();
    } catch (err) {
      console.error("Error loading citations:", err);
    }
  },

  renderCitations() {
    const styleEl = document.getElementById('citation-style');
    const container = document.getElementById('citations-list');
    if (!container || !styleEl || !Array.isArray(this.currentCitations)) return;

    const style = styleEl.value;
    container.innerHTML = '';

    if (this.currentCitations.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted); padding:1rem;">No citations added yet. Click "Add Citation" to add your first reference.</div>';
      return;
    }

    this.currentCitations.forEach((c) => {
      const formattedHtml = this.formatCitationText(c, style, true);
      const formattedPlain = this.formatCitationText(c, style, false);

      const card = document.createElement('div');
      card.className = 'citation-card';
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.6rem;">
          <span class="badge" style="background:var(--accent-indigo, #6366f1); color:#fff; text-transform:uppercase; font-size:0.75rem;">${c.citation_type || 'reference'}</span>
          <button class="btn btn-sm copy-single-cit-btn" title="Copy this citation in ${style} format">
            <i class="fa-regular fa-copy"></i> <span>Copy Citation</span>
          </button>
        </div>
        <div class="formatted-citation">${formattedHtml}</div>
      `;

      const copySingleBtn = card.querySelector('.copy-single-cit-btn');
      if (copySingleBtn) {
        copySingleBtn.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(formattedPlain);
            const span = copySingleBtn.querySelector('span');
            const icon = copySingleBtn.querySelector('i');
            if (span && icon) {
              const origText = span.textContent;
              span.textContent = 'Copied!';
              icon.className = 'fa-solid fa-check';
              copySingleBtn.style.borderColor = 'var(--accent-green, #10b981)';
              copySingleBtn.style.color = 'var(--accent-green, #10b981)';
              setTimeout(() => {
                span.textContent = origText;
                icon.className = 'fa-regular fa-copy';
                copySingleBtn.style.borderColor = '';
                copySingleBtn.style.color = '';
              }, 2000);
            }
          } catch (err) {
            console.error("Failed to copy citation:", err);
          }
        });
      }

      container.appendChild(card);
    });
  },

  // ── FEATURE 14: Resource Library ────────────────────────
  setupResources() {
    const addResForm = document.getElementById('add-resource-form');
    if (addResForm) {
      addResForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          title: document.getElementById('res-title').value,
          category: document.getElementById('res-category').value,
          description: document.getElementById('res-description').value
        };

        await fetch('/api/resources/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        this.closeModal('resource-modal');
        addResForm.reset();
        this.loadResources();
      });
    }
  },

  async loadResources() {
    try {
      const res = await fetch('/api/resources');
      const resources = await res.json();
      const container = document.getElementById('resources-grid');
      if (!container || !Array.isArray(resources)) return;

      container.innerHTML = '';
      resources.forEach(r => {
        const card = document.createElement('div');
        card.className = 'resource-card';
        card.innerHTML = `
          <div>
            <span class="badge" style="background:var(--accent-cyan, #06b6d4); color:#000; font-weight:700;">${r.category}</span>
            <h3 style="margin-top:0.6rem; font-size:1.05rem; font-weight:700; color:var(--text-main);">${r.title}</h3>
            <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.4rem; line-height:1.4;">${r.description}</p>
          </div>
          <a href="/api/download/${r.filename}" class="btn btn-sm btn-outline" style="margin-top:1.2rem; text-decoration:none; justify-content:center; display:inline-flex; align-items:center; gap:6px;">
            <i class="fa-solid fa-download"></i> Download Resource
          </a>
        `;
        container.appendChild(card);
      });
    } catch (err) {
      console.error("Error loading resources:", err);
    }
  },

  // ── FEATURE 15: Peer Thesis Archive ────────────────────
  setupArchive() {
    const searchBtn = document.getElementById('archive-search-btn');
    const searchInput = document.getElementById('archive-search-input');
    const deptFilter = document.getElementById('archive-dept-filter');

    if (searchBtn) searchBtn.addEventListener('click', () => this.loadArchive());
    if (searchInput) searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.loadArchive();
    });
    if (deptFilter) deptFilter.addEventListener('change', () => this.loadArchive());

    const addArchForm = document.getElementById('add-archive-form');
    if (addArchForm) {
      addArchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          title: document.getElementById('arch-title').value,
          author: document.getElementById('arch-author').value,
          department: document.getElementById('arch-dept').value,
          year: parseInt(document.getElementById('arch-year').value || '2026'),
          research_area: document.getElementById('arch-area').value,
          keywords: document.getElementById('arch-keywords').value,
          abstract: document.getElementById('arch-abstract').value
        };

        try {
          const res = await fetch('/api/archive/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            this.closeModal('archive-modal');
            addArchForm.reset();
            this.loadArchive();
          } else {
            alert(data.message || data.error || 'Error adding thesis to archive.');
          }
        } catch (err) {
          console.error("Error adding thesis to archive:", err);
        }
      });
    }
  },

  async loadArchive() {
    try {
      const q = document.getElementById('archive-search-input')?.value || '';
      const dept = document.getElementById('archive-dept-filter')?.value || '';
      const container = document.getElementById('archive-results');
      if (!container) return;

      const res = await fetch(`/api/archive?q=${encodeURIComponent(q)}&dept=${encodeURIComponent(dept)}`);
      const papers = await res.json();
      container.innerHTML = '';

      if (!papers || papers.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted); padding:1rem;">No archived theses found matching the search criteria.</p>';
        return;
      }

      papers.forEach(p => {
        const card = document.createElement('div');
        card.className = 'archive-card';
        card.innerHTML = `
          <h3 style="font-size:1.1rem; font-weight:700; color:var(--accent-pink, #ec4899);">${p.title}</h3>
          <div class="archive-meta">
            <span><i class="fa-solid fa-user"></i> ${p.author}</span> &bull; 
            <span><i class="fa-solid fa-building-columns"></i> ${p.department} (${p.year})</span> &bull;
            <span><i class="fa-solid fa-tag"></i> ${p.research_area}</span>
          </div>
          <p style="font-size:0.88rem; margin:0.6rem 0; line-height:1.45; color:var(--text-main);">${p.abstract}</p>
          <small style="color:var(--accent-cyan, #06b6d4); font-weight:600;">Keywords: ${p.keywords}</small>
        `;
        container.appendChild(card);
      });
    } catch (err) {
      console.error("Error loading archive:", err);
    }
  }
};

// Global expose for modular invocation
window.ThesisHub = ThesisHub;
window.openThesisModal = (id) => ThesisHub.openModal(id);
window.closeThesisModal = (id) => ThesisHub.closeModal(id);
window.loadThesisTracker = () => ThesisHub.loadMilestones();
window.loadOverleafEditor = () => ThesisHub.loadDocument();
window.loadCitationsManager = () => ThesisHub.loadCitations();
window.loadResourceLibrary = () => ThesisHub.loadResources();
window.loadPeerArchive = () => ThesisHub.loadArchive();

document.addEventListener('DOMContentLoaded', () => {
  ThesisHub.init();
});
