let facultySearchTimeout = null;
let currentViewingFaculty = null;

function getCurrentUser() {
  if (window.currentUser) return window.currentUser;
  try {
    const stored = localStorage.getItem('rip_user');
    if (stored) return JSON.parse(stored);
  } catch (e) {}
  return null;
}

function clearAllSearchInputs() {
  const inputs = ['facultySearchInput', 'facultyLabFilter', 'matchingSearchInput', 'availabilitySearchInput', 'labSearchInput', 'finderKeyword'];
  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const selects = ['facultyDeptFilter', 'facultyDomainFilter', 'availDeptFilter', 'availDomainFilter', 'availStatusFilter', 'finderDept'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  // Remove any legacy saved search history from localStorage so nothing is saved anywhere
  try {
    Object.keys(localStorage).forEach(k => {
      if (k.startsWith('rip_search_state_')) {
        localStorage.removeItem(k);
      }
    });
  } catch (e) {}
}

function debounceFacultySearch() {
  clearTimeout(facultySearchTimeout);
  facultySearchTimeout = setTimeout(() => {
    runFacultySearch();
  }, 300);
}

async function runFacultySearch() {
  const keywords = document.getElementById('facultySearchInput')?.value || '';
  const department = document.getElementById('facultyDeptFilter')?.value || '';
  const domain = document.getElementById('facultyDomainFilter')?.value || '';
  const lab = document.getElementById('facultyLabFilter')?.value || '';
  
  const params = new URLSearchParams();
  if (keywords) params.append('keywords', keywords);
  if (department) params.append('department', department);
  if (domain) params.append('domain', domain);
  if (lab) params.append('lab', lab);
  
  try {
    const res = await fetch(`/api/faculty/search?${params.toString()}`);
    const data = await res.json();
    
    if (data.success) {
      renderFacultyList(data.faculties);
    } else {
      console.error(data.message);
    }
  } catch (err) {
    console.error("Error fetching faculty data:", err);
  }
}

function renderFacultyList(faculties) {
  const list = document.getElementById('facultyList');
  const empty = document.getElementById('facultyListEmpty');
  if (!list) return;
  list.innerHTML = '';
  
  if (!faculties || faculties.length === 0) {
    list.style.display = 'none';
    if (empty) empty.style.display = 'block';
    return;
  }
  
  list.style.display = 'grid';
  if (empty) empty.style.display = 'none';
  
  faculties.forEach(fac => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.cursor = 'pointer';
    card.onclick = () => openFacultyDetailsModal(fac.user_id);
    
    // Format domains as plain clean text without square/box background
    const domainsArr = fac.research_domains || [];
    const domainsText = domainsArr.length > 0 
      ? domainsArr.join(', ')
      : 'General Research';
    
    card.innerHTML = `
      <div style="margin-bottom:0.4rem;">
        <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-pink); margin:0;">${fac.name}</h3>
      </div>
      <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.8rem;">${fac.designation}, ${fac.department}</div>
      <div style="margin-bottom:0.8rem;">
        <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.3rem; color:var(--text-main);">Expertise & Research Domains:</div>
        <div style="font-size:0.85rem; color:var(--text-muted); line-height:1.4;">${domainsText}</div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:0.8rem; margin-top:auto;">
        <span style="font-size:0.8rem; color:var(--text-muted);">h-index: <strong>${fac.h_index || 0}</strong></span>
        <span style="font-size:0.8rem; color:var(--text-muted);">Labs: <strong>${(fac.directed_labs || []).length}</strong></span>
        <span style="font-size:0.8rem; color:var(--text-muted);">Pubs: <strong>${(fac.publications || []).length}</strong></span>
      </div>
    `;
    list.appendChild(card);
  });
}

async function openFacultyDetailsModal(facultyId) {
  try {
    const res = await fetch(`/api/faculty/profile?faculty_id=${facultyId}`);
    const data = await res.json();
    if (data.success) {
      currentViewingFaculty = data.faculty;
      window.currentViewingFaculty = data.faculty;
      renderFacultyDetails(data.faculty);
      document.getElementById('facultyDetailsModal').classList.add('open');
    } else {
      alert(data.message);
    }
  } catch (err) {
    console.error(err);
    alert('Error loading profile');
  }
}

function closeFacultyDetailsModal() {
  document.getElementById('facultyDetailsModal').classList.remove('open');
}

function renderFacultyDetails(fac) {
  document.getElementById('facDetailsName').textContent = fac.name;
  document.getElementById('facDetailsDesigDept').textContent = `${fac.designation}, Department of ${fac.department} | ${fac.email}`;
  
  const maxCap = fac.max_capacity !== undefined ? fac.max_capacity : 5;
  const currStud = fac.current_students !== undefined ? fac.current_students : 0;
  const remSlots = fac.remaining_slots !== undefined ? fac.remaining_slots : Math.max(0, maxCap - currStud);

  if (document.getElementById('facDetailsCurrStudents')) document.getElementById('facDetailsCurrStudents').textContent = currStud;
  if (document.getElementById('facDetailsMaxCap')) document.getElementById('facDetailsMaxCap').textContent = maxCap;
  if (document.getElementById('facDetailsSlots')) document.getElementById('facDetailsSlots').textContent = remSlots;
  if (document.getElementById('facDetailsHIndex')) document.getElementById('facDetailsHIndex').textContent = fac.h_index || 0;
  if (document.getElementById('facDetailsCgpa')) document.getElementById('facDetailsCgpa').textContent = fac.min_cgpa_req || 3.0;

  const statusEl = document.getElementById('facDetailsStatusBadge');
  if (statusEl) {
    if (remSlots === 0) {
      statusEl.textContent = 'Full (0 slots)';
      statusEl.style.color = 'var(--text-muted)';
    } else if (remSlots <= 2) {
      statusEl.textContent = `Limited (${remSlots} slots)`;
      statusEl.style.color = 'var(--accent-pink)';
    } else {
      statusEl.textContent = `Available (${remSlots} slots)`;
      statusEl.style.color = 'var(--accent-teal)';
    }
  }
  
  // Format domains as plain clean text without square/box background tags
  const domainsContainer = document.getElementById('facDetailsDomains');
  if (domainsContainer) {
    const domainsList = fac.research_domains || [];
    domainsContainer.innerHTML = domainsList.length > 0 
      ? `<div style="font-size:0.9rem; color:var(--text-main); line-height:1.5;">${domainsList.join(', ')}</div>`
      : `<p style="font-size:0.85rem; color:var(--text-muted); margin:0;">None listed.</p>`;
  }
  
  const labsContainer = document.getElementById('facDetailsLabs');
  if (fac.directed_labs && fac.directed_labs.length > 0) {
    labsContainer.innerHTML = fac.directed_labs.map(l => `
      <div style="background:var(--bg-card); padding:1rem; border-radius:var(--radius); border:1px solid var(--border-color); margin-bottom:0.8rem;">
        <h5 style="font-size:1rem; font-weight:700; color:var(--accent-pink); margin-bottom:0.3rem;">${l.lab_name}</h5>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem;"><strong>Focus Area:</strong> ${l.focus_area}</div>
        ${l.facilities && l.facilities.length > 0 ? `<div style="font-size:0.85rem; color:var(--text-muted);"><strong>Facilities:</strong> ${l.facilities.join(', ')}</div>` : ''}
      </div>
    `).join('');
  } else {
    labsContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--text-muted);">No directed labs.</p>';
  }
  
  const pubsContainer = document.getElementById('facDetailsPublications');
  if (fac.publications && fac.publications.length > 0) {
    pubsContainer.innerHTML = fac.publications.map(p => `
      <div style="background:var(--bg-card); padding:1rem; border-radius:var(--radius); border:1px solid var(--border-color); margin-bottom:0.8rem;">
        <h5 style="font-size:0.95rem; font-weight:700; margin-bottom:0.3rem; color:var(--accent-cyan);">${p.title}</h5>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.3rem;"><strong>Authors:</strong> ${(p.authors || []).join(', ')}</div>
        <div style="font-size:0.85rem; color:var(--text-muted);"><strong>Domain:</strong> ${p.domain} | <strong>Year:</strong> ${p.publication_year}</div>
      </div>
    `).join('');
  } else {
    pubsContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--text-muted);">No publications found.</p>';
  }

  // Edit Profile button visibility (Faculty owner OR Admin)
  const editBtn = document.getElementById('editFacultyProfileBtn');
  const currentUser = getCurrentUser();
  
  const isOwner = currentUser && (currentUser.user_id === fac.user_id || currentUser.user_id === fac.faculty_id);
  const isAdmin = currentUser && currentUser.role === 'Admin';
  
  if (editBtn) {
    if (isOwner || isAdmin) {
      editBtn.style.display = 'inline-block';
    } else {
      editBtn.style.display = 'none';
    }
  }

  // Pre-fill edit modal inputs
  const desigInput = document.getElementById('editFacDesignation');
  if (desigInput) desigInput.value = fac.designation || '';
  const domainsInput = document.getElementById('editFacDomains');
  if (domainsInput) domainsInput.value = (fac.research_domains || []).join(', ');
  const hIndexInput = document.getElementById('editFacHIndex');
  if (hIndexInput) hIndexInput.value = fac.h_index || 0;
  const slotsInput = document.getElementById('editFacSlots');
  if (slotsInput) slotsInput.value = fac.remaining_slots || 0;
  const minCgpaVal = (fac.min_cgpa_req !== undefined && fac.min_cgpa_req !== null) ? fac.min_cgpa_req : (fac.min_cgpa !== undefined ? fac.min_cgpa : 3.0);
  const cgpaInput = document.getElementById('editFacCgpa');
  if (cgpaInput) cgpaInput.value = minCgpaVal;
  const minCgpaInput = document.getElementById('editFacMinCgpa');
  if (minCgpaInput) minCgpaInput.value = minCgpaVal;
  const thesisInput = document.getElementById('editFacThesisAvail');
  if (thesisInput) thesisInput.checked = !!fac.thesis_available;
}

function openEditFacultyModal() {
  closeFacultyDetailsModal();
  document.getElementById('editFacultyProfileModal')?.classList.add('open');
}

function closeEditFacultyModal() {
  document.getElementById('editFacultyProfileModal')?.classList.remove('open');
}

async function submitEditFacultyProfile() {
  const currentUser = getCurrentUser();
  const targetId = (currentViewingFaculty && (currentViewingFaculty.user_id || currentViewingFaculty.faculty_id)) || window._editingAvailabilityFacultyId || (currentUser ? currentUser.user_id : null);
  if (!targetId) return;

  const designation = document.getElementById('editFacDesignation')?.value.trim() || '';
  const domains = (document.getElementById('editFacDomains')?.value || '').split(',').map(s => s.trim()).filter(Boolean);
  const hIndex = parseInt(document.getElementById('editFacHIndex')?.value) || 0;
  const slots = parseInt(document.getElementById('editFacSlots')?.value) || 0;
  
  const cgpaEl = document.getElementById('editFacCgpa') || document.getElementById('editFacMinCgpa');
  const cgpaVal = cgpaEl ? cgpaEl.value : '';
  const cgpa = (cgpaVal !== '' && !isNaN(parseFloat(cgpaVal))) ? parseFloat(cgpaVal) : 3.0;

  const thesisAvail = document.getElementById('editFacThesisAvail')?.checked ? 1 : 0;
  const endpoint = (currentUser && currentUser.role === 'Admin') ? '/api/faculty/admin_edit' : '/api/faculty/update_profile';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        faculty_id: targetId,
        designation: designation,
        research_domains: domains,
        h_index: hIndex,
        remaining_slots: slots,
        min_cgpa_req: cgpa,
        min_cgpa: cgpa,
        thesis_available: thesisAvail
      })
    });
    const data = await res.json();
    if (data.success) {
      if (window.showToast) window.showToast('Faculty profile updated successfully!');
      else alert('Profile updated successfully!');
      closeEditFacultyModal();
      if (typeof openFacultyDetailsModal === 'function') openFacultyDetailsModal(targetId);
      if (typeof runFacultySearch === 'function') runFacultySearch();
      if (typeof window.runAvailabilitySearch === 'function') window.runAvailabilitySearch();
    } else {
      alert(data.message || 'Error updating profile');
    }
  } catch (e) {
    console.error(e);
    alert('Error updating profile');
  }
}

// Ensure the functions are exposed globally
window.getCurrentUser = getCurrentUser;
window.runFacultySearch = runFacultySearch;
window.debounceFacultySearch = debounceFacultySearch;
window.openFacultyDetailsModal = openFacultyDetailsModal;
window.closeFacultyDetailsModal = closeFacultyDetailsModal;
window.openEditFacultyModal = openEditFacultyModal;
window.closeEditFacultyModal = closeEditFacultyModal;
window.submitEditFacultyProfile = submitEditFacultyProfile;
window.clearAllSearchInputs = clearAllSearchInputs;
window.loadUserSearchState = clearAllSearchInputs;
window.saveUserSearchState = function() {}; // No-op, do not save searches anywhere

document.addEventListener('DOMContentLoaded', () => {
    clearAllSearchInputs();
    runFacultySearch();
});
