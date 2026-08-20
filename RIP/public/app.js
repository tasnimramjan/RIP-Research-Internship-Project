document.addEventListener('DOMContentLoaded', () => {
  // Tab Switching
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.getAttribute('data-tab');
      document.getElementById(targetTab).classList.add('active');
    });
  });

  // FEATURE 11: MILESTONES & AI ASSISTANT
  const milestoneModal = document.getElementById('milestone-modal');
  const openMilestoneModalBtn = document.getElementById('open-milestone-modal-btn');
  const closeMilestoneModalBtn = document.getElementById('close-milestone-modal-btn');
  const addMilestoneForm = document.getElementById('add-milestone-form');

  if (openMilestoneModalBtn) {
    openMilestoneModalBtn.addEventListener('click', () => milestoneModal.classList.remove('hidden'));
  }
  if (closeMilestoneModalBtn) {
    closeMilestoneModalBtn.addEventListener('click', () => milestoneModal.classList.add('hidden'));
  }

  if (addMilestoneForm) {
    addMilestoneForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById('ms-title').value,
        phase: document.getElementById('ms-phase').value,
        due_date: document.getElementById('ms-date').value,
        progress: 0,
        status: 'Pending'
      };

      await fetch('/api/milestones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      milestoneModal.classList.add('hidden');
      addMilestoneForm.reset();
      loadMilestones();
    });
  }

  async function loadMilestones() {
    const res = await fetch('/api/milestones');
    const data = await res.json();
    const container = document.getElementById('milestones-list');
    if (!container) return;

    container.innerHTML = '';
    let totalProgress = 0;

    data.forEach(item => {
      totalProgress += item.progress;
      const card = document.createElement('div');
      card.className = 'milestone-card';
      card.innerHTML = `
        <div class="milestone-header">
          <span>${item.title} <small>(${item.phase})</small></span>
          <span class="badge ${item.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${item.status}</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${item.progress}%"></div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <small style="color:var(--text-muted)">Progress: ${item.progress}% | Due: ${item.due_date}</small>
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

    document.querySelectorAll('.prog-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = e.target.getAttribute('data-id');
        const newProg = parseInt(e.target.getAttribute('data-prog'));
        const newStatus = newProg >= 100 ? 'Completed' : (newProg > 0 ? 'In Progress' : 'Pending');

        await fetch('/api/milestones/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, progress: newProg, status: newStatus })
        });
        loadMilestones();
      });
    });
  }

  // AI Assistant Interaction
  const aiSubmitBtn = document.getElementById('ai-submit-btn');
  const aiPrompt = document.getElementById('ai-input-prompt');
  const chatHistory = document.getElementById('ai-chat-history');

  if (aiSubmitBtn) {
    aiSubmitBtn.addEventListener('click', async () => {
      const text = aiPrompt.value.trim();
      if (!text) return;

      const userMsg = document.createElement('div');
      userMsg.className = 'chat-message user';
      userMsg.textContent = text;
      chatHistory.appendChild(userMsg);

      aiPrompt.value = '';
      chatHistory.scrollTop = chatHistory.scrollHeight;

      const res = await fetch('/api/ai-assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text, context: '' })
      });
      const data = await res.json();

      const aiMsg = document.createElement('div');
      aiMsg.className = 'chat-message ai';
      aiMsg.innerText = data.response;
      chatHistory.appendChild(aiMsg);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    });
  }

  // FEATURE 12: OVERLEAF EDITOR & SUPERVISOR APPROVAL
  let currentDocId = 1;
  const latexInput = document.getElementById('latex-input');
  const latexPreview = document.getElementById('latex-preview');
  const supervisorModal = document.getElementById('supervisor-modal');
  const editFeedbackBtn = document.getElementById('edit-feedback-btn');
  const closeSupervisorModalBtn = document.getElementById('close-supervisor-modal-btn');
  const supervisorForm = document.getElementById('supervisor-form');

  if (editFeedbackBtn) editFeedbackBtn.addEventListener('click', () => supervisorModal.classList.remove('hidden'));
  if (closeSupervisorModalBtn) closeSupervisorModalBtn.addEventListener('click', () => supervisorModal.classList.add('hidden'));

  async function loadDocument() {
    const res = await fetch('/api/documents');
    const docs = await res.json();
    if (docs.length > 0) {
      const doc = docs[0];
      currentDocId = doc.id;
      if (latexInput) latexInput.value = doc.content;
      const verBadge = document.getElementById('doc-version-badge');
      if (verBadge) verBadge.textContent = doc.version;
      
      updateSupervisorUI(doc.status, doc.supervisor_feedback);
      renderLatexPreview(doc.content);
    }
  }

  function updateSupervisorUI(status, feedback) {
    const statusBadge = document.getElementById('supervisor-status-badge');
    const feedbackText = document.getElementById('supervisor-feedback-text');

    if (statusBadge && feedbackText) {
      statusBadge.textContent = status;
      feedbackText.textContent = feedback || 'No comments provided.';

      statusBadge.className = 'badge ';
      if (status === 'Approved') statusBadge.classList.add('badge-success');
      else if (status === 'Needs Revision') statusBadge.classList.add('badge-warning');
      else statusBadge.classList.add('badge-danger');
    }

    const sel = document.getElementById('sup-status-select');
    const inp = document.getElementById('sup-feedback-input');
    if (sel) sel.value = status;
    if (inp) inp.value = feedback || '';
  }

  if (supervisorForm) {
    supervisorForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const status = document.getElementById('sup-status-select').value;
      const feedback = document.getElementById('sup-feedback-input').value;

      await fetch('/api/documents/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: currentDocId, status, feedback })
      });

      updateSupervisorUI(status, feedback);
      supervisorModal.classList.add('hidden');
    });
  }

  function renderLatexPreview(code) {
    if (!latexPreview) return;
    let html = code
      .replace(/\\documentclass\{.*?\}/g, '')
      .replace(/\\title\{(.*?)\}/g, '<h1>$1</h1>')
      .replace(/\\author\{(.*?)\}/g, '<p style="text-align:center;"><strong>Author:</strong> $1</p>')
      .replace(/\\date\{(.*?)\}/g, '<p style="text-align:center; color:gray;">$1</p>')
      .replace(/\\begin\{document\}/g, '')
      .replace(/\\end\{document\}/g, '')
      .replace(/\\maketitle/g, '<hr style="margin:15px 0;">')
      .replace(/\\section\{(.*?)\}/g, '<h2>$1</h2>')
      .replace(/\\subsection\{(.*?)\}/g, '<h3>$1</h3>')
      .replace(/\\textbf\{(.*?)\}/g, '<strong>$1</strong>')
      .replace(/\\textit\{(.*?)\}/g, '<em>$1</em>')
      .replace(/\n\n/g, '<p></p>');

    latexPreview.innerHTML = html;
  }

  if (latexInput) {
    latexInput.addEventListener('input', (e) => renderLatexPreview(e.target.value));
  }

  const saveBtn = document.getElementById('save-doc-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      await fetch('/api/documents/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: currentDocId, content: latexInput.value, version: 'v1.3' })
      });
      alert('Document saved!');
    });
  }

  // FEATURE 13: CITATIONS
  let currentCitations = [];

  async function loadCitations() {
    const res = await fetch('/api/citations');
    currentCitations = await res.json();
    renderCitations();
  }

  function renderCitations() {
    const styleEl = document.getElementById('citation-style');
    const container = document.getElementById('citations-list');
    if (!container || !styleEl) return;

    const style = styleEl.value;
    container.innerHTML = '';

    currentCitations.forEach(c => {
      let formatted = '';
      if (style === 'APA') {
        formatted = `${c.authors} (${c.year}). ${c.title}. <em>${c.journal || ''}</em>. DOI: ${c.doi || 'N/A'}`;
      } else if (style === 'IEEE') {
        formatted = `${c.authors}, "${c.title}," <em>${c.journal || ''}</em>, ${c.year}.`;
      } else if (style === 'MLA') {
        formatted = `${c.authors}. "${c.title}." <em>${c.journal || ''}</em>, ${c.year}.`;
      } else if (style === 'BibTeX') {
        formatted = `@article{ref_${c.id},\n  author = {${c.authors}},\n  title = {${c.title}},\n  year = {${c.year}}\n}`;
      }

      const card = document.createElement('div');
      card.className = 'citation-card';
      card.innerHTML = `<span class="badge">${c.citation_type}</span><div class="formatted-citation">${formatted}</div>`;
      container.appendChild(card);
    });
  }

  const styleSelect = document.getElementById('citation-style');
  if (styleSelect) styleSelect.addEventListener('change', renderCitations);

  const citModal = document.getElementById('citation-modal');
  const openCitBtn = document.getElementById('open-citation-modal-btn');
  const closeCitBtn = document.getElementById('close-citation-modal-btn');

  if (openCitBtn) openCitBtn.addEventListener('click', () => citModal.classList.remove('hidden'));
  if (closeCitBtn) closeCitBtn.addEventListener('click', () => citModal.classList.add('hidden'));

  const addCitForm = document.getElementById('add-citation-form');
  if (addCitForm) {
    addCitForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById('cit-title').value,
        authors: document.getElementById('cit-authors').value,
        year: parseInt(document.getElementById('cit-year').value),
        journal: document.getElementById('cit-journal').value,
        doi: document.getElementById('cit-doi').value,
        citation_type: document.getElementById('cit-type').value
      };

      await fetch('/api/citations/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      citModal.classList.add('hidden');
      loadCitations();
    });
  }

  // FEATURE 14: RESOURCES & MODAL HANDLERS
  const resModal = document.getElementById('resource-modal');
  const openResBtn = document.getElementById('open-resource-modal-btn');
  const closeResBtn = document.getElementById('close-resource-modal-btn');
  const addResForm = document.getElementById('add-resource-form');

  if (openResBtn) openResBtn.addEventListener('click', () => resModal.classList.remove('hidden'));
  if (closeResBtn) closeResBtn.addEventListener('click', () => resModal.classList.add('hidden'));

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

      if (resModal) resModal.classList.add('hidden');
      addResForm.reset();
      loadResources();
    });
  }

  async function loadResources() {
    const res = await fetch('/api/resources');
    const resources = await res.json();
    const container = document.getElementById('resources-grid');
    if (!container) return;

    container.innerHTML = '';
    resources.forEach(r => {
      const card = document.createElement('div');
      card.className = 'resource-card';
      card.innerHTML = `
        <div>
          <span class="badge">${r.category}</span>
          <h3 style="margin-top:8px;">${r.title}</h3>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-top:6px;">${r.description}</p>
        </div>
        <a href="/api/download/${r.filename}" class="btn btn-sm btn-outline" style="margin-top:16px; text-decoration:none; justify-content:center; display:inline-flex; align-items:center; gap:6px;">
          <i class="fa-solid fa-download"></i> Download Resource
        </a>
      `;
      container.appendChild(card);
    });
  }

  // FEATURE 15: ARCHIVE
  async function loadArchive() {
    const qEl = document.getElementById('archive-search-input');
    const deptEl = document.getElementById('archive-dept-filter');
    const container = document.getElementById('archive-results');
    if (!container) return;

    const q = qEl ? qEl.value : '';
    const dept = deptEl ? deptEl.value : '';

    const res = await fetch(`/api/archive?q=${encodeURIComponent(q)}&dept=${encodeURIComponent(dept)}`);
    const papers = await res.json();
    container.innerHTML = '';

    if (papers.length === 0) {
      container.innerHTML = '<p style="color:gray;">No papers found.</p>';
      return;
    }

    papers.forEach(p => {
      const card = document.createElement('div');
      card.className = 'archive-card';
      card.innerHTML = `
        <h3>${p.title}</h3>
        <div class="archive-meta">
          <span>${p.author}</span> | <span>${p.department} (${p.year})</span>
        </div>
        <p style="font-size:0.9rem; margin:8px 0;">${p.abstract}</p>
        <small style="color:var(--primary-color);">Keywords: ${p.keywords}</small>
      `;
      container.appendChild(card);
    });
  }

  const searchBtn = document.getElementById('archive-search-btn');
  if (searchBtn) searchBtn.addEventListener('click', loadArchive);

  // Initialize
  loadMilestones();
  loadDocument();
  loadCitations();
  loadResources();
  loadArchive();
});