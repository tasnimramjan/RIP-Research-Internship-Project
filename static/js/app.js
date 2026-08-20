// ==========================================================
// R.I.P. Platform v2 — Client Router (MVC View Layer)
// Removed features:
//   1. Research Interest Matching & 1-to-1 Supervisor Chat
//   2. Faculty Profile Explorer
//   3. Availability Tracker
//   4. Project Teammate Finder
//   5. Discussion Forums & Thread Reminders
// Kept features:
//   - Smart Supervisor Finder
//   - Research Lab Board
//   - Internship Opportunity Portal
//   - Research Paper Discovery
//   - Thesis Group Finder
//   - Admin Control Panel
// ==========================================================

let currentUser = null;
let chatPollInterval = null;

document.addEventListener('DOMContentLoaded', () => { initApp(); });

function initApp() {
  const stored = localStorage.getItem('rip_user');
  currentUser = stored ? JSON.parse(stored) : null;
  renderUserNav();
  showLandingPage();
  if (currentUser && window.Forums) Forums.init(currentUser);
  if (currentUser && window.Teammates) Teammates.init(currentUser);
}

// ── Navigation ──────────────────────────────────────────
function renderUserNav() {
  const container     = document.getElementById('userNavStatus');
  const burgerBtn     = document.getElementById('hamburgerBtn');
  const adminMenuItem = document.getElementById('adminMenuItem');
  if (!container) return;

  if (currentUser) {
    if (burgerBtn)     burgerBtn.style.display = 'inline-flex';
    if (adminMenuItem) adminMenuItem.style.display = (currentUser.role === 'Admin') ? 'block' : 'none';

    // Thesis Group Finder: hidden for Faculty
    const thesisMenuItem = document.getElementById('thesisGroupMenuItem');
    if (thesisMenuItem) thesisMenuItem.style.display = (currentUser.role === 'Faculty') ? 'none' : 'block';

    container.innerHTML = `
      <div class="user-chip">
        <span style="font-weight:600;">${currentUser.name}</span>
        <span class="role-pill role-${currentUser.role}">${currentUser.role}</span>
      </div>
      <button class="btn btn-sm btn-secondary" onclick="logout()">Log Out</button>`;
  } else {
    if (burgerBtn)     burgerBtn.style.display = 'none';
    if (adminMenuItem) adminMenuItem.style.display = 'none';
    closeMenuDrawer();
    container.innerHTML = `
      <button class="btn btn-sm btn-cyan"      onclick="openAuthModal('login')">Log In</button>
      <button class="btn btn-sm btn-secondary" onclick="openAuthModal('signup')">Sign Up</button>`;
  }
}

function toggleMenuDrawer() {
  document.getElementById('menuDrawer')?.classList.toggle('open');
}
function closeMenuDrawer() {
  document.getElementById('menuDrawer')?.classList.remove('open');
}

function showLandingPage() {
  closeMenuDrawer();
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('landing-panel')?.classList.add('active');

  const authSection = document.getElementById('landingAuthSection');
  if (!authSection) return;
  if (currentUser) {
    authSection.innerHTML = `
      <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); padding:1rem 1.5rem; border-radius:10px; text-align:center;">
        <p style="font-size:1.1rem; font-weight:700; color:var(--accent-cyan);">Welcome back, ${currentUser.name}</p>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.3rem;">Role: ${currentUser.role} &bull; Department: ${currentUser.department}</p>
        <p style="font-size:0.82rem; color:var(--text-main); margin-top:0.8rem;">Click the menu icon in the top right navigation bar to access features.</p>
      </div>`;
  } else {
    authSection.innerHTML = `
      <div class="landing-auth-buttons">
        <button class="btn btn-cyan"      onclick="openAuthModal('login')">Log In</button>
        <button class="btn btn-secondary" onclick="openAuthModal('signup')">Sign Up</button>
      </div>`;
  }
}

function switchView(viewId) {
  closeMenuDrawer();
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  document.getElementById(viewId)?.classList.add('active');

  if      (viewId === 'supervisor-finder') loadSupervisors();
  else if (viewId === 'lab-board')         loadLabBoard();
  else if (viewId === 'internship-portal') loadInternships();
  else if (viewId === 'paper-discovery')   loadPapers();
  else if (viewId === 'thesis-groups')     loadThesisGroups();
  else if (viewId === 'admin-panel')       loadAdminPanel();
  else if (viewId === 'availability-tracker') loadAvailabilityTracker();
  else if (viewId === 'discussion-forums' && window.Forums) Forums.loadThreads();
  else if (viewId === 'teammate-finder' && window.Teammates) Teammates.loadProjects();
}

// ── Authentication ───────────────────────────────────────
function openAuthModal(mode = 'login') { toggleAuthMode(mode); document.getElementById('authModal').classList.add('open'); }
function closeAuthModal()              { document.getElementById('authModal').classList.remove('open'); }

function toggleAuthMode(mode) {
  const isSignup = mode === 'signup';
  document.getElementById('loginForm').style.display  = isSignup ? 'none'  : 'block';
  document.getElementById('signupForm').style.display = isSignup ? 'block' : 'none';
  document.getElementById('authModalTitle').innerText = isSignup ? 'Create Account' : 'Account Login';
}

async function submitLogin() {
  const email    = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!email || !password) return alert('Please enter your email and password.');
  const res  = await fetch('/api/auth/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email, password}) });
  const data = await res.json();
  if (data.success) { currentUser = data.user; localStorage.setItem('rip_user', JSON.stringify(currentUser)); renderUserNav(); closeAuthModal(); showLandingPage(); if(window.Forums) Forums.init(currentUser); if(window.Teammates) Teammates.init(currentUser); }
  else alert(data.message);
}

async function submitSignup() {
  const name     = document.getElementById('signupName').value.trim();
  const email    = document.getElementById('signupEmail').value.trim();
  const password = document.getElementById('signupPassword').value;
  const role     = document.getElementById('signupRole').value;
  const dept     = document.getElementById('signupDept').value;
  if (!name || !email || !password) return alert('Name, email, and password are required.');
  if (password.length < 8) return alert('Password must be at least 8 characters long.');
  const res  = await fetch('/api/auth/signup', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, email, password, role, department: dept}) });
  const data = await res.json();
  if (data.success) { currentUser = data.user; localStorage.setItem('rip_user', JSON.stringify(currentUser)); renderUserNav(); closeAuthModal(); showLandingPage(); if(window.Forums) Forums.init(currentUser); if(window.Teammates) Teammates.init(currentUser); }
  else alert(data.message);
}

function logout() { currentUser = null; localStorage.removeItem('rip_user'); if(window.Forums && window.Forums.pollingInterval) clearInterval(window.Forums.pollingInterval); if(window.Teammates && window.Teammates.pollingInterval) clearInterval(window.Teammates.pollingInterval); renderUserNav(); showLandingPage(); }

// ── FEATURE 1: Smart Supervisor Finder ──────────────────
async function loadSupervisors() {
  const dept  = document.getElementById('finderDept')?.value    || '';
  const kw    = document.getElementById('finderKeyword')?.value || '';
  const cgpa  = document.getElementById('finderCgpa')?.value    || '';
  const avail = document.getElementById('finderAvail')?.checked || false;
  const res   = await fetch(`/api/supervisors/search?department=${dept}&keyword=${kw}&cgpa=${cgpa}&availability_only=${avail}`);
  const data  = await res.json();
  const container = document.getElementById('supervisorList');
  if (!container) return;
  if (!data.supervisors?.length) {
    container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; padding:2rem;">No supervisors match the specified criteria.</p>`; return;
  }
  container.innerHTML = data.supervisors.map(f => `
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <div class="card-title">${f.name}</div>
          <div style="font-size:0.8rem; color:var(--accent-cyan); font-weight:600;">${f.designation} - ${f.department}</div>
        </div>
        <span class="tag" style="background:rgba(99,102,241,0.2); color:var(--accent-indigo);">h-index: ${f.h_index}</span>
      </div>
      <div class="tags-list">${f.research_domains.map(d => `<span class="tag">${d}</span>`).join('')}</div>
      <div style="font-size:0.82rem; color:var(--text-muted); display:flex; justify-content:space-between; margin-top:0.4rem;">
        <span>Min CGPA: <strong>${f.min_cgpa_req}</strong></span>
        <span>Slots: <strong style="color:${f.remaining_slots > 0 ? '#10b981' : '#ef4444'};">${f.remaining_slots > 0 ? f.remaining_slots + ' Available' : 'Full'}</strong></span>
      </div>
      <div style="font-size:0.78rem; color:var(--text-muted);">Contact: ${f.email}</div>
    </div>`).join('');
}

// ── FEATURE 2: Research Lab Board ───────────────────────
async function loadLabBoard() {
  const searchName = document.getElementById('labSearchInput')?.value.trim() || '';
  const res  = await fetch(`/api/labs/all?name=${encodeURIComponent(searchName)}`);
  const data = await res.json();
  const container = document.getElementById('labList');
  const isAdmin   = currentUser?.role === 'Admin';
  const isFaculty = currentUser?.role === 'Faculty';
  const btn = document.getElementById('createLabBtn');
  if (btn) btn.style.display = isFaculty ? 'inline-flex' : 'none';
  if (!data.labs?.length) {
    container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; padding:2rem;">No research labs found.</p>`; return;
  }
  container.innerHTML = data.labs.map(l => {
    const isOwner = currentUser && (currentUser.user_id === l.faculty_id || isAdmin);
    return `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.4rem;">
          <div>
            <div class="card-title">${l.lab_name}</div>
            <div style="font-size:0.85rem; color:var(--accent-cyan);">Director: ${l.faculty_name} (${l.department})</div>
          </div>
          ${isAdmin ? `<button class="btn btn-sm btn-danger" onclick="adminDeleteLab('${l.lab_id}')">Delete Lab</button>` : ''}
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted);">${l.focus_area}</p>
        <div>
          <div style="font-size:0.72rem; color:var(--text-muted); font-weight:700; margin-bottom:0.3rem;">FACILITIES</div>
          <div class="tags-list">${l.facilities.map(f => `<span class="tag">${f}</span>`).join('')}</div>
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin:0.5rem 0 0.3rem;">
            <span style="font-size:0.72rem; color:var(--text-muted); font-weight:700;">ONGOING PROJECTS</span>
            ${isOwner ? `<button class="btn btn-sm btn-secondary" style="font-size:0.7rem; padding:0.2rem 0.5rem;" onclick="openAddLabProjectModal('${l.lab_id}')">+ Add Project</button>` : ''}
          </div>
          ${l.ongoing_projects.length ? l.ongoing_projects.map(p => `<div style="font-size:0.82rem; background:rgba(255,255,255,0.04); padding:0.5rem 0.7rem; border-radius:6px; margin-bottom:0.3rem;">${p.title}</div>`).join('') : `<p style="font-size:0.78rem; color:var(--text-muted);">No projects listed.</p>`}
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin:0.5rem 0 0.3rem;">
            <span style="font-size:0.72rem; color:var(--text-muted); font-weight:700;">RA OPPORTUNITIES</span>
            ${isOwner ? `<button class="btn btn-sm btn-cyan" style="font-size:0.7rem; padding:0.2rem 0.5rem;" onclick="openPostRaModal('${l.lab_id}')">+ Post RA Position</button>` : ''}
          </div>
          ${l.ra_opportunities.length ? l.ra_opportunities.map(ra => `
            <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); padding:0.6rem; border-radius:6px; margin-bottom:0.4rem;">
              <div style="font-weight:700; font-size:0.85rem;">${ra.title}</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">${ra.description}</div>
              <div style="font-size:0.75rem; color:var(--accent-cyan); margin-top:0.2rem;">Stipend: ${ra.stipend} | Deadline: ${ra.deadline}</div>
            </div>`).join('') : `<p style="font-size:0.78rem; color:var(--text-muted);">No RA positions open.</p>`}
        </div>
      </div>`;
  }).join('');
}

function openCreateLabModal() { if (!currentUser || currentUser.role !== 'Faculty') return alert('Only Faculty can create research labs.'); document.getElementById('createLabModal').classList.add('open'); }
function closeCreateLabModal() { document.getElementById('createLabModal').classList.remove('open'); }
async function submitCreateLab() {
  if (!currentUser || currentUser.role !== 'Faculty') return;
  const name = document.getElementById('newLabName').value.trim();
  const area = document.getElementById('newLabArea').value.trim();
  const facilities = document.getElementById('newLabFacilities').value.trim();
  if (!name || !area) return alert('Lab name and focus area are required.');
  const res = await fetch('/api/faculty/create_lab', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({faculty_id: currentUser.user_id, lab_name: name, focus_area: area, facilities}) });
  const data = await res.json();
  if (data.success) { alert('Research lab created successfully.'); closeCreateLabModal(); loadLabBoard(); } else alert(data.message);
}

let activeLabForProject = null;
function openAddLabProjectModal(labId) { activeLabForProject = labId; document.getElementById('addLabProjectModal').classList.add('open'); }
function closeAddLabProjectModal()     { document.getElementById('addLabProjectModal').classList.remove('open'); }
async function submitAddLabProject() {
  const title = document.getElementById('newProjectLabTitle').value.trim();
  const desc  = document.getElementById('newProjectLabDesc').value.trim();
  if (!title || !activeLabForProject) return alert('Project title is required.');
  const res = await fetch('/api/faculty/add_project', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({lab_id: activeLabForProject, title, description: desc}) });
  const data = await res.json();
  alert(data.message); closeAddLabProjectModal(); loadLabBoard();
}

let activeLabForRa = null;
function openPostRaModal(labId) { activeLabForRa = labId; document.getElementById('postRaModal').classList.add('open'); }
function closePostRaModal()     { document.getElementById('postRaModal').classList.remove('open'); }
async function submitPostRa() {
  const title   = document.getElementById('newRaTitle').value.trim();
  const desc    = document.getElementById('newRaDesc').value.trim();
  const stipend = document.getElementById('newRaStipend').value.trim();
  const deadline= document.getElementById('newRaDeadline').value.trim();
  if (!title || !desc || !activeLabForRa) return alert('Title and description are required.');
  const res = await fetch('/api/labs/post_ra', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({lab_id: activeLabForRa, title, description: desc, stipend, deadline}) });
  const data = await res.json();
  alert(data.message); closePostRaModal(); loadLabBoard();
}

// ── FEATURE 3: Internship Opportunity Portal (KEPT) ─────
async function loadInternships() {
  const studentId = currentUser?.user_id || '';
  const res  = await fetch(`/api/internships/all?student_id=${studentId}`);
  const data = await res.json();
  const container = document.getElementById('internshipList');
  const isStudent = currentUser?.role === 'Student';
  const isAdmin   = currentUser?.role === 'Admin';
  const adminBtn  = document.getElementById('adminAddInternshipBtn');
  if (adminBtn) adminBtn.style.display = isAdmin ? 'inline-flex' : 'none';

  container.innerHTML = data.opportunities.map(int => {
    const eligBadge = isStudent
      ? `<span class="tag" style="background:${int.eligible ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}; color:${int.eligible ? '#10b981' : '#ef4444'}; font-weight:700;">${int.eligible ? 'ELIGIBLE' : 'INELIGIBLE (CGPA)'}</span>` : '';
    return `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.4rem;">
          <div>
            <div class="card-title">${int.title}</div>
            <div style="font-size:0.85rem; color:var(--accent-indigo); font-weight:700;">Company: ${int.company_name}</div>
          </div>
          <div style="display:flex; gap:0.4rem; align-items:center;">
            ${eligBadge}
            ${isAdmin ? `<button class="btn btn-sm btn-danger" onclick="adminDeleteInternship('${int.opportunity_id}')">Delete</button>` : ''}
          </div>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted);">${int.requirements}</p>
        <div style="font-size:0.8rem; color:var(--text-muted); display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.3rem;">
          <span>Min CGPA: <strong>${int.min_cgpa}</strong></span>
          <span>Deadline: <strong>${int.deadline}</strong></span>
        </div>
        <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.25); border-radius:8px; padding:0.7rem 1rem; margin-top:0.5rem;">
          <div style="font-size:0.75rem; font-weight:700; color:var(--accent-indigo); margin-bottom:0.4rem;">CONTACT INFORMATION</div>
          ${int.contact_email ? `<div style="font-size:0.83rem; margin-bottom:0.2rem;">Email: <a href="mailto:${int.contact_email}" style="color:var(--accent-cyan);">${int.contact_email}</a></div>` : ''}
          ${int.contact_phone ? `<div style="font-size:0.83rem;">Phone: <strong>${int.contact_phone}</strong></div>` : ''}
        </div>
      </div>`;
  }).join('');
}

function openAdminAddInternshipModal() { document.getElementById('adminInternshipModal').classList.add('open'); }
function closeAdminAddInternshipModal(){ document.getElementById('adminInternshipModal').classList.remove('open'); }
async function submitAdminAddInternship() {
  const company  = document.getElementById('adminIntCompany').value.trim();
  const title    = document.getElementById('adminIntTitle').value.trim();
  const reqs     = document.getElementById('adminIntReqs').value.trim();
  const cgpa     = document.getElementById('adminIntCgpa').value;
  const dept     = document.getElementById('adminIntDept').value;
  const deadline = document.getElementById('adminIntDeadline').value;
  const email    = document.getElementById('adminIntEmail').value.trim();
  const phone    = document.getElementById('adminIntPhone').value.trim();
  if (!company || !title || !reqs || !deadline) return alert('Company, title, requirements, and deadline are required.');
  const res = await fetch('/api/admin/create_internship', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({company_name: company, title, requirements: reqs, min_cgpa: cgpa, department: dept, deadline, contact_email: email, contact_phone: phone}) });
  const data = await res.json();
  if (data.success) { alert('Internship opportunity created.'); closeAdminAddInternshipModal(); loadInternships(); } else alert(data.message);
}
async function adminDeleteInternship(oppId) {
  if (!confirm('Are you sure you want to delete this internship posting?')) return;
  const res = await fetch('/api/admin/delete_internship', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({opportunity_id: oppId}) });
  const data = await res.json();
  alert(data.message); loadInternships();
}

// ── FEATURE 4: Research Paper Discovery ─────────────────
async function loadPapers() {
  const author = document.getElementById('paperAuthorFilter')?.value.trim() || '';
  const domain = document.getElementById('paperDomainFilter')?.value || '';
  const year   = document.getElementById('paperYearFilter')?.value || '';
  const kw     = document.getElementById('paperSearchInput')?.value.trim() || '';
  const res    = await fetch(`/api/papers/search?author=${encodeURIComponent(author)}&domain=${encodeURIComponent(domain)}&year=${encodeURIComponent(year)}&keyword=${encodeURIComponent(kw)}`);
  const data   = await res.json();
  const dl = document.getElementById('paperSuggestions');
  if (dl) dl.innerHTML = (data.papers || []).map(p => `<option value="${p.title}">`).join('');
  renderPapers(data.papers);
}

function runPaperSearch() { loadPapers(); }

function renderPapers(papers) {
  const container = document.getElementById('paperList');
  if (!papers?.length) { container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; padding:2rem;">No research papers found matching your criteria.</p>`; return; }
  container.innerHTML = papers.map(p => `
    <div class="card">
      <div class="card-title" style="font-size:0.98rem;">${p.title}</div>
      <div style="font-size:0.78rem; color:var(--accent-cyan);">Authors: ${p.authors.join(', ')} (${p.publication_year})</div>
      <div style="font-size:0.75rem; background:rgba(99,102,241,0.15); color:var(--accent-indigo); padding:0.15rem 0.5rem; border-radius:5px; display:inline-block;">${p.domain}</div>
      <p style="font-size:0.82rem; color:var(--text-muted); line-height:1.5;">${p.abstract}</p>
      <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-top:0.4rem;">
        <button class="btn btn-sm btn-secondary" onclick="exportCitation('${p.paper_id}','IEEE')">IEEE Citation</button>
        <button class="btn btn-sm btn-secondary" onclick="exportCitation('${p.paper_id}','APA')">APA Citation</button>
        <button class="btn btn-sm btn-secondary" onclick="exportCitation('${p.paper_id}','MLA')">MLA Citation</button>
      </div>
    </div>`).join('');
}

async function exportCitation(paperId, style) {
  const res  = await fetch(`/api/papers/citation?paper_id=${paperId}&style=${style}`);
  const data = await res.json();
  document.getElementById('citationStyle').innerText  = style + ' Citation';
  document.getElementById('citationOutput').innerText = data.citation;
  document.getElementById('citationModal').classList.add('open');
}
function closeCitationModal() { document.getElementById('citationModal').classList.remove('open'); }
function copyCitation() { navigator.clipboard.writeText(document.getElementById('citationOutput').innerText).then(() => alert('Citation copied to clipboard.')); }

// ── FEATURE 5: Thesis Group Finder ──────────────────────
async function loadThesisGroups() {
  const topic = document.getElementById('groupSearchInput')?.value || '';
  const res   = await fetch(`/api/thesis_groups/all?topic=${encodeURIComponent(topic)}`);
  const data  = await res.json();
  const container = document.getElementById('thesisGroupList');
  const isAdmin   = currentUser?.role === 'Admin';
  if (!data.groups?.length) { container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; padding:2rem;">No thesis groups found.</p>`; return; }
  container.innerHTML = data.groups.map(g => {
    const alreadyMember = currentUser && g.members.some(m => m.student_id === currentUser.user_id);
    const canJoin = currentUser?.role === 'Student';
    return `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div class="card-title">${g.group_name}</div>
          ${isAdmin ? `<button class="btn btn-sm btn-danger" onclick="adminDeleteThesisGroup('${g.group_id}')">Delete Group</button>` : ''}
        </div>
        <div style="font-size:0.8rem; color:var(--accent-cyan); font-weight:700;">Topic: ${g.topic}</div>
        <p style="font-size:0.85rem; color:var(--text-muted);">${g.description}</p>
        <div style="font-size:0.8rem; color:var(--text-muted);">Creator: <strong>${g.creator_name}</strong> | Members: <strong>${g.members.length}</strong></div>
        <div class="tags-list" style="margin-top:0.3rem;">${g.members.map(m => `<span class="tag">Member: ${m.student_name}</span>`).join('')}</div>
        <div style="display:flex; gap:0.5rem; margin-top:0.8rem; flex-wrap:wrap;">
          ${canJoin && !alreadyMember ? `<button class="btn btn-sm btn-cyan" onclick="joinThesisGroup('${g.group_id}')">Join Study Circle</button>` : ''}
          ${alreadyMember ? `<span class="tag" style="background:rgba(16,185,129,0.2); color:#10b981; font-weight:700;">Member</span>` : ''}
          ${alreadyMember ? `<button class="btn btn-sm btn-danger" onclick="leaveThesisGroup('${g.group_id}')">Leave Study Circle</button>` : ''}
          ${currentUser ? `<button class="btn btn-sm btn-secondary" onclick="openChat('${g.group_id}','${g.group_name}')">Group Chat</button>` : ''}
        </div>
      </div>`;
  }).join('');
}

async function joinThesisGroup(groupId) {
  if (currentUser?.role !== 'Student') return alert('Only Students can join thesis groups.');
  const res = await fetch('/api/thesis_groups/join', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({group_id: groupId, student_id: currentUser.user_id}) });
  const data = await res.json(); alert(data.message); loadThesisGroups();
}
async function leaveThesisGroup(groupId) {
  if (!currentUser) return; if (!confirm('Leave this study circle?')) return;
  const res = await fetch('/api/thesis_groups/leave', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({group_id: groupId, student_id: currentUser.user_id}) });
  const data = await res.json(); alert(data.message); loadThesisGroups();
}
function openNewGroupModal() {
  if (currentUser?.role !== 'Student') return alert(currentUser ? 'Only Students can create thesis groups.' : 'Please log in as a Student.');
  document.getElementById('newGroupModal').classList.add('open');
}
function closeNewGroupModal() { document.getElementById('newGroupModal').classList.remove('open'); }
async function submitNewGroup() {
  const groupName = document.getElementById('newGroupName').value.trim();
  const topic     = document.getElementById('newGroupTopic').value.trim();
  const desc      = document.getElementById('newGroupDesc').value.trim();
  if (!groupName || !topic || !desc) return alert('All fields are required.');
  const res = await fetch('/api/thesis_groups/create', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({group_name: groupName, topic, description: desc, student_id: currentUser.user_id}) });
  const data = await res.json();
  if (data.success) { alert(`Study circle "${groupName}" created.`); closeNewGroupModal(); loadThesisGroups(); } else alert(data.message);
}

// ── Faculty Profile Update (accessible from Lab Board) ──
function openEditFacultyProfileModal() { if (currentUser?.role !== 'Faculty') return; document.getElementById('editFacultyProfileModal').classList.add('open'); }
function closeEditFacultyProfileModal(){ document.getElementById('editFacultyProfileModal').classList.remove('open'); }
async function submitEditFacultyProfile() {
  if (currentUser?.role !== 'Faculty') return;
  const res = await fetch('/api/faculty/update_profile', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({
    faculty_id: currentUser.user_id,
    designation: document.getElementById('editFacDesignation').value.trim(),
    h_index: document.getElementById('editFacHIndex').value,
    research_domains: document.getElementById('editFacDomains').value.trim(),
    remaining_slots: document.getElementById('editFacSlots').value,
    min_cgpa_req: document.getElementById('editFacMinCgpa').value,
    thesis_available: document.getElementById('editFacThesisAvail').checked
  })});
  const data = await res.json(); alert(data.message); closeEditFacultyProfileModal();
}

// ── Admin Control Panel ──────────────────────────────────
async function loadAdminPanel() {
  if (!currentUser || currentUser.role !== 'Admin') { alert('Access restricted to System Administrators.'); showLandingPage(); return; }
  const [statsRes, usersRes] = await Promise.all([fetch('/api/admin/analytics'), fetch('/api/admin/users')]);
  const { stats: s = {} } = await statsRes.json();
  const { users = [] }    = await usersRes.json();

  document.getElementById('adminStatsContainer').innerHTML = `
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:1rem; width:100%;">
      ${[['Total Users', s.total_users||0, 'cyan'], ['Students', s.total_students||0, 'indigo'], ['Faculty', s.total_faculty||0, 'purple'], ['Research Labs', s.total_labs||0, 'pink'], ['Internships', s.total_internships||0, '#10b981'], ['Thesis Groups', s.total_groups||0, '#f59e0b']].map(([label, val, color]) => `
      <div style="background:rgba(6,182,212,0.06); border:1px solid rgba(255,255,255,0.1); padding:1rem; border-radius:8px; text-align:center;">
        <div style="font-size:0.75rem; color:var(--text-muted);">${label}</div>
        <div style="font-size:1.8rem; font-weight:800; color:var(--accent-${color}, ${color});">${val}</div>
      </div>`).join('')}
    </div>`;

  const tbody = document.getElementById('adminUsersTableBody');
  if (tbody) tbody.innerHTML = users.map(u => `
    <tr style="border-bottom:1px solid var(--border-color);">
      <td style="padding:0.75rem 0.5rem; font-weight:600;">${u.name}</td>
      <td style="padding:0.75rem 0.5rem; color:var(--text-muted);">${u.email}</td>
      <td style="padding:0.75rem 0.5rem;"><span class="role-pill role-${u.role}">${u.role}</span></td>
      <td style="padding:0.75rem 0.5rem;">${u.department}</td>
      <td style="padding:0.75rem 0.5rem;">
        <span class="tag" style="background:${(u.status||'Active')==='Active'?'rgba(16,185,129,0.2)':'rgba(239,68,68,0.2)'}; color:${(u.status||'Active')==='Active'?'#10b981':'#ef4444'};">${u.status||'Active'}</span>
      </td>
      <td style="padding:0.75rem 0.5rem;">
        <div style="display:flex; gap:0.4rem;">
          <button class="btn btn-sm btn-secondary" onclick="adminToggleUserStatus('${u.user_id}')">${(u.status||'Active')==='Active'?'Suspend':'Activate'}</button>
          <button class="btn btn-sm btn-danger"    onclick="adminDeleteUser('${u.user_id}')">Delete</button>
        </div>
      </td>
    </tr>`).join('');
}

async function adminToggleUserStatus(userId) { const res = await fetch('/api/admin/toggle_user', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:userId})}); const data=await res.json(); alert(data.message); loadAdminPanel(); }
async function adminDeleteUser(userId) { if(!confirm('Delete this user?'))return; const res=await fetch('/api/admin/delete_user',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:userId})}); const data=await res.json(); alert(data.message); loadAdminPanel(); }
function openAddUserModal()  { document.getElementById('addUserModal').classList.add('open'); }
function closeAddUserModal() { document.getElementById('addUserModal').classList.remove('open'); }
async function submitAddUser() {
  const name=document.getElementById('addUserName').value.trim(), email=document.getElementById('addUserEmail').value.trim(), password=document.getElementById('addUserPassword').value, role=document.getElementById('addUserRole').value, dept=document.getElementById('addUserDept').value;
  if(!name||!email||!password)return alert('Name, email, and password are required.');
  const res=await fetch('/api/admin/add_user',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,email,password,role,department:dept})});
  const data=await res.json(); if(data.success){alert(data.message);closeAddUserModal();loadAdminPanel();}else alert(data.message);
}
async function adminDeleteLab(labId) { if(!confirm('Delete this lab?'))return; const res=await fetch('/api/admin/delete_lab',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lab_id:labId})}); const data=await res.json(); alert(data.message); loadLabBoard(); }
async function adminDeleteThesisGroup(groupId) { if(!confirm('Delete this group?'))return; const res=await fetch('/api/admin/delete_group',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({group_id:groupId})}); const data=await res.json(); alert(data.message); loadThesisGroups(); }

// ── Group Chat Drawer ────────────────────────────────────
function openChat(groupId, name) {
  if (!currentUser) return alert('Please log in to send messages.');
  document.getElementById('chatHeaderTitle').innerText = 'Group Chat: ' + name;
  document.getElementById('chatDrawer').classList.add('open');
  window._activeGroupId = groupId;
  fetchChatMessages();
  if (chatPollInterval) clearInterval(chatPollInterval);
  chatPollInterval = setInterval(fetchChatMessages, 2500);
}
function closeChat() { document.getElementById('chatDrawer').classList.remove('open'); window._activeGroupId = null; if(chatPollInterval)clearInterval(chatPollInterval); }

async function fetchChatMessages() {
  if (!window._activeGroupId || !currentUser) return;
  const res  = await fetch(`/api/chat/group?group_id=${window._activeGroupId}`);
  const data = await res.json();
  const container = document.getElementById('chatMessages');
  if (!data.messages) return;
  container.innerHTML = data.messages.map(m => {
    const mine = m.sender_id === currentUser.user_id;
    return `<div class="chat-bubble ${mine?'mine':'other'}">
      <div style="font-size:0.68rem;opacity:0.8;font-weight:700;">${m.sender_name}</div>
      <div>${m.message_text}</div>
      <div style="font-size:0.65rem;opacity:0.6;text-align:right;margin-top:0.2rem;">${m.timestamp.substring(11,16)}</div>
    </div>`;
  }).join('');
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text || !window._activeGroupId) return;
  await fetch('/api/chat/group/send', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({sender_id: currentUser.user_id, group_id: window._activeGroupId, text}) });
  input.value = ''; fetchChatMessages();
}

// FEATURE 5: Availability Tracker
async function loadAvailabilityTracker() {
  const container = document.getElementById('trackerContainer');
  if(!container) return;
  container.innerHTML = '<div style="color:var(--text-muted);">Loading availability data...</div>';
  
  try {
    const res = await fetch('/api/supervisors/search');
    const data = await res.json();
    
    if (!data.supervisors || data.supervisors.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted);">No faculty data available.</div>';
      return;
    }
    
    container.innerHTML = data.supervisors.map(f => {
      const isAvailable = f.thesis_available === 1 && f.remaining_slots > 0;
      const badgeClass = isAvailable ? 'available' : 'full';
      const badgeText = isAvailable ? 'Accepting Students' : 'Full / Unavailable';
      
      return `
        <div class="tracker-card">
          <div class="tracker-header">
            <div>
              <h3 style="margin-bottom:0.2rem; font-size:1.2rem;">${f.name}</h3>
              <div style="font-size:0.9rem; color:var(--text-muted);">${f.designation} &bull; ${f.department}</div>
            </div>
            <div class="tracker-badge ${badgeClass}">${badgeText}</div>
          </div>
          <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom: 0.5rem;">
            Min CGPA Required: <strong style="color:var(--text-color);">${f.min_cgpa_req}</strong>
          </div>
          <div class="tracker-slots">
            <h3>${f.remaining_slots}</h3>
            <p>Estimated Slots Left</p>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="color:red;">Error loading availability data.</div>';
  }
}

