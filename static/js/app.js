// ==========================================================
// R.I.P. Platform - Member 1
// Features: Authentication, Nav, Landing, Supervisor Finder, Lab Board
// ==========================================================

let currentUser = null;

document.addEventListener('DOMContentLoaded', () => { initApp(); });

function initApp() {
  const stored = localStorage.getItem('rip_user');
  currentUser = stored ? JSON.parse(stored) : null;
  renderUserNav();
  showLandingPage();
}

function renderUserNav() {
  const container = document.getElementById('userNavStatus');
  const burgerBtn = document.getElementById('hamburgerBtn');
  if (!container) return;

  if (currentUser) {
    if (burgerBtn) burgerBtn.style.display = 'inline-flex';
    container.innerHTML = `
      <div class="user-chip">
        <span style="font-weight:600;">${currentUser.name}</span>
        <span class="role-pill role-${currentUser.role}">${currentUser.role}</span>
      </div>
      <button class="btn btn-sm btn-secondary" onclick="logout()">Log Out</button>`;
  } else {
    if (burgerBtn) burgerBtn.style.display = 'none';
    closeMenuDrawer();
    container.innerHTML = `
      <button class="btn btn-sm btn-cyan"      onclick="openAuthModal('login')">Log In</button>
      <button class="btn btn-sm btn-secondary" onclick="openAuthModal('signup')">Sign Up</button>`;
  }
}

function toggleMenuDrawer() { document.getElementById('menuDrawer')?.classList.toggle('open'); }
function closeMenuDrawer()  { document.getElementById('menuDrawer')?.classList.remove('open'); }

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
}

// Authentication
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
  if (data.success) { currentUser = data.user; localStorage.setItem('rip_user', JSON.stringify(currentUser)); renderUserNav(); closeAuthModal(); showLandingPage(); }
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
  if (data.success) { currentUser = data.user; localStorage.setItem('rip_user', JSON.stringify(currentUser)); renderUserNav(); closeAuthModal(); showLandingPage(); }
  else alert(data.message);
}

function logout() { currentUser = null; localStorage.removeItem('rip_user'); renderUserNav(); showLandingPage(); }

// FEATURE 1: Smart Supervisor Finder
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

// FEATURE 2: Research Lab Board
async function loadLabBoard() {
  const searchName = document.getElementById('labSearchInput')?.value.trim() || '';
  const res  = await fetch(`/api/labs/all?name=${encodeURIComponent(searchName)}`);
  const data = await res.json();
  const container = document.getElementById('labList');
  const isFaculty = currentUser?.role === 'Faculty';
  const btn = document.getElementById('createLabBtn');
  if (btn) btn.style.display = isFaculty ? 'inline-flex' : 'none';
  if (!data.labs?.length) {
    container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; padding:2rem;">No research labs found.</p>`; return;
  }
  container.innerHTML = data.labs.map(l => {
    const isOwner = currentUser && (currentUser.user_id === l.faculty_id);
    return `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.4rem;">
          <div>
            <div class="card-title">${l.lab_name}</div>
            <div style="font-size:0.85rem; color:var(--accent-cyan);">Director: ${l.faculty_name} (${l.department})</div>
          </div>
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
