let matchingSearchTimeout = null;

function getUser() {
  if (window.getCurrentUser) return window.getCurrentUser();
  if (window.currentUser) return window.currentUser;
  const stored = localStorage.getItem('rip_user');
  if (stored) {
    try { return JSON.parse(stored); } catch (e) {}
  }
  return null;
}

function debounceMatchingSearch() {
  clearTimeout(matchingSearchTimeout);
  matchingSearchTimeout = setTimeout(() => {
    runMatchingSearch();
  }, 300);
}

async function runMatchingSearch() {
  const keywordsInput = document.getElementById('matchingSearchInput');
  const keywords = keywordsInput ? keywordsInput.value.trim() : '';
  const emptyState = document.getElementById('matchingEmptyState');
  const resultsContainer = document.getElementById('matchingResultsContainer');
  
  const user = getUser();
  let studentId = '';
  if (user && user.role && user.role.toLowerCase() === 'student') {
    studentId = user.user_id;
  }
  
  try {
    const res = await fetch(`/api/matching/search?keywords=${encodeURIComponent(keywords)}&student_id=${encodeURIComponent(studentId)}`);
    const data = await res.json();
    
    if (data.success) {
      renderMatchingResults(data);
    } else {
      console.error("Matching API error:", data.message);
    }
  } catch (err) {
    console.error("Error fetching matching data:", err);
  }
}

function renderMatchingResults(data) {
  const emptyState = document.getElementById('matchingEmptyState');
  const resultsContainer = document.getElementById('matchingResultsContainer');
  
  const { faculty = [], labs = [], theses = [], projects = [] } = data;
  
  if (faculty.length === 0 && labs.length === 0 && theses.length === 0 && projects.length === 0) {
    emptyState.style.display = 'block';
    emptyState.textContent = 'No matching faculty or research records found. Try adjusting your query.';
    resultsContainer.style.display = 'none';
    return;
  }
  
  emptyState.style.display = 'none';
  resultsContainer.style.display = 'flex';
  
  const currentUser = getUser();
  const isStudent = currentUser && currentUser.role && currentUser.role.toLowerCase() === 'student';
  const canMessageFaculty = isStudent;
  
  // Render Faculty
  const facList = document.getElementById('matchFacultyList');
  if (facList) {
    if (faculty.length > 0) {
      facList.style.display = 'grid';
      facList.innerHTML = faculty.map(f => {
        const score = f.match_score || 80;
        const availableText = (f.thesis_available === 1 && f.remaining_slots > 0) ? 
          `<span style="color:#10b981; font-weight:600;">Open (${f.remaining_slots} slots)</span>` : 
          `<span style="color:#ef4444; font-weight:600;">Full / Closed</span>`;
          
        const messageBtn = canMessageFaculty ? 
          `<button class="btn btn-sm btn-cyan" onclick="openDirectChat('${f.faculty_id}', '${f.name.replace(/'/g, "\\'")}')">Message</button>` : '';

        // Match percentage badge visible ONLY to students in matching faculty section
        const matchBadge = isStudent ? 
          `<span class="badge" style="background:rgba(6,182,212,0.12); color:var(--accent-cyan); border:1px solid rgba(6,182,212,0.3); border-radius:12px; padding:0.3rem 0.75rem; font-weight:700; font-size:0.78rem; display:inline-flex; align-items:center; justify-content:center; text-align:center; white-space:nowrap; box-sizing:border-box;">${score}% Match</span>` : '';

        return `
          <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.6rem;">
              <div>
                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                  <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-cyan); margin:0;">${f.name}</h3>
                  ${matchBadge}
                </div>
                <div style="font-size:0.85rem; color:var(--text-muted); margin-top:0.2rem;">${f.designation}, ${f.department}</div>
              </div>
              ${messageBtn}
            </div>
            
            <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.6rem;">
              Min CGPA Req: <strong>${f.min_cgpa_req}</strong> &bull; Status: ${availableText}
            </div>

            <div style="margin-bottom:0.4rem;">
              <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Research Domains:</div>
              <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
                ${(f.research_domains || []).map(d => `<span class="badge" style="background:var(--bg-lighter); color:var(--text-main); border:1px solid var(--border-color); border-radius:8px; padding:0.2rem 0.5rem; font-size:0.76rem;">${d}</span>`).join('')}
              </div>
            </div>
          </div>
        `;
      }).join('');
    } else {
      facList.innerHTML = '<p style="color:var(--text-muted);">No faculty found matching these keywords.</p>';
      facList.style.display = 'block';
    }
  }
  
  // Render Labs
  const labList = document.getElementById('matchLabList');
  if (labList) {
    if (labs.length > 0) {
      labList.style.display = 'grid';
      labList.innerHTML = labs.map(l => `
        <div class="card">
          <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-indigo); margin-bottom:0.2rem;">${l.lab_name}</h3>
          <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.6rem;">Director: ${l.faculty_name}</div>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.8rem;">${l.focus_area}</p>
          <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Facilities:</div>
          <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
            ${(l.facilities || []).map(f => `<span class="badge" style="background:rgba(99,102,241,0.1); color:var(--accent-indigo); border:1px solid rgba(99,102,241,0.2); border-radius:8px; padding:0.2rem 0.5rem; font-size:0.76rem;">${f}</span>`).join('')}
          </div>
        </div>
      `).join('');
    } else {
      labList.innerHTML = '<p style="color:var(--text-muted);">No research labs found matching these keywords.</p>';
      labList.style.display = 'block';
    }
  }
  
  // Render Thesis
  const thesisList = document.getElementById('matchThesisList');
  if (thesisList) {
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
      thesisList.innerHTML = '<p style="color:var(--text-muted);">No previous thesis found matching these keywords.</p>';
      thesisList.style.display = 'block';
    }
  }
  
  // Render Projects
  const projList = document.getElementById('matchProjectList');
  if (projList) {
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
}

async function loadFacultyMatchedStudents() {
  const user = getUser();
  if (!user || !user.role || user.role.toLowerCase() !== 'faculty') return;
  const container = document.getElementById('facultyMatchedStudentsList');
  if (!container) return;
  
  container.innerHTML = '<div style="color:var(--text-muted);">Loading matched students...</div>';
  try {
    const res = await fetch(`/api/matching/students?faculty_id=${user.user_id}`);
    const data = await res.json();
    if (!data.students || data.students.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted);">No student matches found yet.</div>';
      return;
    }
    container.innerHTML = data.students.map(s => {
      const interests = (s.research_interests || []).map(i => `<span class="badge" style="background:var(--bg-lighter); color:var(--text-main);">${i}</span>`).join(' ');
      return `
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                <h4 style="margin:0; font-size:1rem; font-weight:800; color:var(--accent-indigo);">${s.name}</h4>
                <span class="badge" style="background:rgba(99,102,241,0.12); color:var(--accent-indigo); border:1px solid rgba(99,102,241,0.3); border-radius:12px; padding:0.3rem 0.75rem; font-weight:700; font-size:0.78rem; display:inline-flex; align-items:center; justify-content:center; text-align:center; white-space:nowrap; box-sizing:border-box;">${s.match_score}% Match</span>
              </div>
              <div style="font-size:0.83rem; color:var(--text-muted); margin-top:0.2rem;">CGPA: <strong>${s.cgpa}</strong> &bull; Dept: ${s.department}</div>
            </div>
            <button class="btn btn-sm btn-cyan" onclick="openDirectChat('${s.student_id}', '${s.name.replace(/'/g, "\\'")}')">Chat with Student</button>
          </div>
          <div style="margin-top:0.6rem;">
            <div style="font-size:0.78rem; font-weight:600; color:var(--text-muted); margin-bottom:0.3rem;">Student Interests:</div>
            <div style="display:flex; flex-wrap:wrap; gap:0.3rem;">${interests || 'None specified'}</div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="color:red;">Error loading matched students.</div>';
  }
}

async function loadFacultyConversations() {
  const user = getUser();
  if (!user || !user.role || user.role.toLowerCase() !== 'faculty') return;
  const container = document.getElementById('facultyConversationsList');
  if (!container) return;
  
  container.innerHTML = '<div style="color:var(--text-muted);">Loading student messages...</div>';
  try {
    const res = await fetch(`/api/messages/conversations?user_id=${user.user_id}`);
    const data = await res.json();
    if (!data.conversations || data.conversations.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted); padding:0.8rem; text-align:center;">No student messages received yet.</div>';
      return;
    }
    container.innerHTML = data.conversations.map(c => {
      return `
        <div class="card" style="border-left:3px solid var(--accent-cyan);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <h4 style="margin:0; font-size:1rem; font-weight:800; color:var(--accent-cyan);">${c.name}</h4>
              <div style="font-size:0.83rem; color:var(--text-muted); margin-top:0.2rem;">${c.department} &bull; CGPA: <strong>${c.cgpa || 'N/A'}</strong></div>
            </div>
            <button class="btn btn-sm btn-cyan" onclick="openDirectChat('${c.user_id}', '${c.name.replace(/'/g, "\\'")}')">Reply / Chat</button>
          </div>
          <div style="margin-top:0.6rem; padding:0.5rem; background:var(--bg-lighter); border-radius:var(--radius); font-size:0.85rem;">
            <strong>Latest Message:</strong> "${c.last_message}"
            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.2rem;">${c.last_timestamp}</div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="color:red;">Error loading student messages.</div>';
  }
}

function loadInterestMatching() {
  const facultySec = document.getElementById('facultyMatchingSection');
  if (facultySec) facultySec.style.display = 'none';
  
  const user = getUser();
  const roleLower = user && user.role ? user.role.toLowerCase() : '';
  if (roleLower === 'faculty') {
    if (facultySec) facultySec.style.display = 'block';
    loadFacultyConversations();
    loadFacultyMatchedStudents();
  }
  
  // ALWAYS trigger search on page/tab open so faculty, labs, thesis, and projects display immediately for ALL user roles
  runMatchingSearch();
}

// Global exposure
window.runMatchingSearch = runMatchingSearch;
window.debounceMatchingSearch = debounceMatchingSearch;
window.loadFacultyMatchedStudents = loadFacultyMatchedStudents;
window.loadFacultyConversations = loadFacultyConversations;
window.loadInterestMatching = loadInterestMatching;
