let matchingSearchTimeout = null;

function debounceMatchingSearch() {
  clearTimeout(matchingSearchTimeout);
  matchingSearchTimeout = setTimeout(() => {
    runMatchingSearch();
  }, 300);
}

async function runMatchingSearch() {
  const keywords = document.getElementById('matchingSearchInput').value.trim();
  const emptyState = document.getElementById('matchingEmptyState');
  const resultsContainer = document.getElementById('matchingResultsContainer');
  
  if (!keywords) {
    emptyState.style.display = 'block';
    emptyState.textContent = 'Type some keywords above to find matching research opportunities.';
    resultsContainer.style.display = 'none';
    return;
  }
  
  try {
    const res = await fetch(`/api/matching/search?keywords=${encodeURIComponent(keywords)}`);
    const data = await res.json();
    
    if (data.success) {
      renderMatchingResults(data);
    } else {
      console.error(data.message);
    }
  } catch (err) {
    console.error("Error fetching matching data:", err);
  }
}

function renderMatchingResults(data) {
  const emptyState = document.getElementById('matchingEmptyState');
  const resultsContainer = document.getElementById('matchingResultsContainer');
  
  const { faculty, labs, theses, projects } = data;
  
  if (faculty.length === 0 && labs.length === 0 && theses.length === 0 && projects.length === 0) {
    emptyState.style.display = 'block';
    emptyState.textContent = 'No results found. Try adjusting your keywords.';
    resultsContainer.style.display = 'none';
    return;
  }
  
  emptyState.style.display = 'none';
  resultsContainer.style.display = 'flex';
  
  // Render Faculty
  const facList = document.getElementById('matchFacultyList');
  if (faculty.length > 0) {
    facList.style.display = 'grid';
    facList.innerHTML = faculty.map(f => `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-cyan); margin-bottom:0.2rem;">${f.name}</h3>
            <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.6rem;">${f.designation}, ${f.department}</div>
          </div>
          <button class="btn btn-sm btn-cyan" onclick="openDirectChat('${f.faculty_id}', '${f.name.replace(/'/g, "\\'")}')">Message</button>
        </div>
        <div style="margin-bottom:0.8rem;">
          <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Research Domains:</div>
          <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
            ${f.research_domains.map(d => `<span class="badge" style="background:var(--bg-lighter); color:var(--text-main);">${d}</span>`).join('')}
          </div>
        </div>
      </div>
    `).join('');
  } else {
    facList.innerHTML = '<p style="color:var(--text-muted);">No faculty found matching these keywords.</p>';
    facList.style.display = 'block';
  }
  
  // Render Labs
  const labList = document.getElementById('matchLabList');
  if (labs.length > 0) {
    labList.style.display = 'grid';
    labList.innerHTML = labs.map(l => `
      <div class="card">
        <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-indigo); margin-bottom:0.2rem;">${l.lab_name}</h3>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.6rem;">Director: ${l.faculty_name}</div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.8rem;">${l.focus_area}</p>
        <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Facilities:</div>
        <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
          ${l.facilities.map(f => `<span class="badge" style="background:rgba(99,102,241,0.1); color:var(--accent-indigo); border:1px solid rgba(99,102,241,0.2);">${f}</span>`).join('')}
        </div>
      </div>
    `).join('');
  } else {
    labList.innerHTML = '<p style="color:var(--text-muted);">No research labs found matching these keywords.</p>';
    labList.style.display = 'block';
  }
  
  // Render Theses
  const thesisList = document.getElementById('matchThesisList');
  if (theses.length > 0) {
    thesisList.style.display = 'grid';
    thesisList.innerHTML = theses.map(t => `
      <div class="card">
        <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-pink); margin-bottom:0.2rem;">${t.group_name}</h3>
        <div style="font-size:0.85rem; color:var(--text-muted); font-weight:600; margin-bottom:0.6rem;">Topic: ${t.topic}</div>
        <p style="font-size:0.85rem; color:var(--text-muted);">${t.description}</p>
      </div>
    `).join('');
  } else {
    thesisList.innerHTML = '<p style="color:var(--text-muted);">No previous theses found matching these keywords.</p>';
    thesisList.style.display = 'block';
  }
  
  // Render Projects
  const projList = document.getElementById('matchProjectList');
  if (projects.length > 0) {
    projList.style.display = 'grid';
    projList.innerHTML = projects.map(p => `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-cyan); margin-bottom:0.2rem;">${p.title}</h3>
          <span class="badge" style="background:var(--bg-lighter); color:var(--text-main); font-weight:700;">${p.type}</span>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.6rem; margin-top:0.6rem;">${p.description}</p>
        <div style="font-size:0.8rem; color:var(--text-muted);">
          <strong>${p.type === 'Lab Project' ? 'Lab:' : 'Required Skills:'}</strong> ${p.context}
        </div>
      </div>
    `).join('');
  } else {
    projList.innerHTML = '<p style="color:var(--text-muted);">No projects found matching these keywords.</p>';
    projList.style.display = 'block';
  }
}

// Global exposure
window.runMatchingSearch = runMatchingSearch;
window.debounceMatchingSearch = debounceMatchingSearch;

function loadInterestMatching() {
  // Auto-fill research interests if the user is a student
  if (window.currentUser && window.currentUser.role === 'Student' && window.currentUser.student_profile) {
    const interests = window.currentUser.student_profile.research_interests || '';
    const input = document.getElementById('matchingSearchInput');
    if (interests && !input.value) {
      input.value = interests;
      runMatchingSearch();
    }
  }
}
window.loadInterestMatching = loadInterestMatching;
