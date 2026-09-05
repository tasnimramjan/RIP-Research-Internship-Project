let availSearchTimeout = null;

function debounceAvailabilitySearch() {
  clearTimeout(availSearchTimeout);
  availSearchTimeout = setTimeout(() => {
    runAvailabilitySearch();
  }, 300);
}

async function runAvailabilitySearch() {
  const keywords = document.getElementById('availabilitySearchInput')?.value.trim() || '';
  const dept = document.getElementById('availDeptFilter')?.value || '';
  const domain = document.getElementById('availDomainFilter')?.value || '';
  const status = document.getElementById('availStatusFilter')?.value || '';
  
  const emptyState = document.getElementById('availabilityEmptyState');
  const container = document.getElementById('trackerContainer');
  
  if (!container) return;
  
  try {
    const params = new URLSearchParams();
    if (keywords) params.append('keywords', keywords);
    if (dept) params.append('department', dept);
    if (domain) params.append('domain', domain);
    if (status) params.append('status', status);
    
    const res = await fetch(`/api/availability/search?${params.toString()}`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    
    if (data.success) {
      renderAvailabilityResults(data.results);
    } else {
      console.error(data.message || data.error);
    }
  } catch (err) {
    console.error("Error fetching availability data:", err);
    container.style.display = 'block';
    container.innerHTML = `<div style="text-align:center; padding:3rem; color:red;">Failed to connect to the server. Please ensure the server is running.</div>`;
    if (emptyState) emptyState.style.display = 'none';
  }
}

function renderAvailabilityResults(results) {
  const emptyState = document.getElementById('availabilityEmptyState');
  const container = document.getElementById('trackerContainer');
  
  if (!results || results.length === 0) {
    if (emptyState) emptyState.style.display = 'block';
    container.style.display = 'none';
    return;
  }
  
  if (emptyState) emptyState.style.display = 'none';
  container.style.display = 'grid';
  
  const currentUser = window.currentUser || (window.getCurrentUser ? window.getCurrentUser() : null);
  const userRole = currentUser && currentUser.role ? currentUser.role.toLowerCase() : '';
  const isAdmin = userRole === 'admin';

  container.innerHTML = results.map(f => {
    const maxCap = f.max_capacity !== undefined ? f.max_capacity : 5;
    const currStud = f.current_students !== undefined ? f.current_students : 0;

    let remSlots = Math.max(0, maxCap - currStud);
    if (remSlots === 0) {
      f.status = 'Full';
    } else if (remSlots <= 2) {
      f.status = 'Limited';
    } else {
      f.status = 'Available';
    }
    f.remaining_slots = remSlots;

    // Determine badge colors based on status
    let badgeColor = '';
    let badgeBg = '';
    if (f.status === 'Available') {
      badgeColor = 'var(--accent-teal)';
      badgeBg = 'rgba(20,184,166,0.1)';
    } else if (f.status === 'Limited') {
      badgeColor = 'var(--accent-pink)';
      badgeBg = 'rgba(236,72,153,0.1)';
    } else {
      badgeColor = 'var(--text-muted)';
      badgeBg = 'var(--bg-lighter)';
    }
    
    const canUpdate = isAdmin || (userRole === 'faculty' && currentUser && currentUser.user_id === f.faculty_id);
    const domains = f.research_domains || [];

    return `
      <div class="card" style="border-left: 4px solid ${badgeColor};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
          <div>
            <h3 style="font-size:1.1rem; font-weight:800; color:var(--text-main); margin-bottom:0.2rem;">${f.name}</h3>
            <div style="font-size:0.85rem; color:var(--text-muted);">${f.designation}, ${f.department}</div>
          </div>
          <span class="badge" style="background:${badgeBg}; color:${badgeColor}; font-weight:700;">${f.status}</span>
        </div>
        
        <div style="margin-bottom:0.8rem;">
          <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Research Domains:</div>
          <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
            ${domains.slice(0, 3).map(d => `<span class="badge" style="background:var(--bg-lighter); color:var(--text-main);">${d}</span>`).join('')}
            ${domains.length > 3 ? `<span class="badge" style="background:var(--bg-lighter); color:var(--text-muted);">+${domains.length - 3} more</span>` : ''}
          </div>
        </div>
        
        ${f.lab_name ? `
        <div style="font-size:0.8rem; margin-bottom:1rem; color:var(--text-muted);">
          <strong>Lab:</strong> ${f.lab_name}
        </div>
        ` : ''}
        
        <div style="background:var(--bg-main); border-radius:var(--radius); padding:0.8rem; display:flex; justify-content:space-between; text-align:center; margin-bottom:1rem;">
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:var(--text-main);">${currStud}</div>
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Current</div>
          </div>
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:var(--text-main);">${maxCap}</div>
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Max Capacity</div>
          </div>
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:${badgeColor};">${remSlots}</div>
            <div style="font-size:0.7rem; color:${badgeColor}; text-transform:uppercase; letter-spacing:0.5px;">Remaining</div>
          </div>
        </div>
        
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-sm btn-secondary" style="flex:1;" onclick="openViewFacultyDetailsModal('${f.faculty_id}')">View Details</button>
          ${canUpdate ? `<button class="btn btn-sm btn-cyan" style="flex:1;" onclick="openUpdateAvailabilityModal('${f.faculty_id}')">Update</button>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

async function openUpdateAvailabilityModal(facultyId) {
  window._editingAvailabilityFacultyId = facultyId;
  window.currentViewingFaculty = { faculty_id: facultyId, user_id: facultyId };
  try {
    const res = await fetch(`/api/faculty/profile?faculty_id=${facultyId}`);
    const data = await res.json();
    if (data.success && data.faculty) {
      const fac = data.faculty;
      window.currentViewingFaculty = fac;
      const modal = document.getElementById('editFacultyProfileModal');
      if (modal) {
        if (document.getElementById('editFacDesignation')) document.getElementById('editFacDesignation').value = fac.designation || '';
        if (document.getElementById('editFacDomains')) document.getElementById('editFacDomains').value = (fac.research_domains || []).join(', ');
        if (document.getElementById('editFacHIndex')) document.getElementById('editFacHIndex').value = fac.h_index || 0;
        if (document.getElementById('editFacMaxCap')) document.getElementById('editFacMaxCap').value = fac.max_capacity !== undefined ? fac.max_capacity : 5;
        if (document.getElementById('editFacCurrStud')) document.getElementById('editFacCurrStud').value = fac.current_students !== undefined ? fac.current_students : 0;
        if (document.getElementById('editFacSlots')) document.getElementById('editFacSlots').value = fac.remaining_slots !== undefined ? fac.remaining_slots : 0;
        
        const minCgpaVal = fac.min_cgpa_req !== undefined ? fac.min_cgpa_req : 3.0;
        if (document.getElementById('editFacCgpa')) document.getElementById('editFacCgpa').value = minCgpaVal;
        if (document.getElementById('editFacMinCgpa')) document.getElementById('editFacMinCgpa').value = minCgpaVal;
        
        if (document.getElementById('editFacThesisAvail')) document.getElementById('editFacThesisAvail').checked = !!fac.thesis_available;
        
        modal.classList.add('open');
      }
    }
  } catch (err) {
    console.error(err);
  }
}

async function openViewFacultyDetailsModal(facultyId) {
  if (typeof window.openFacultyDetailsModal === 'function') {
    window.openFacultyDetailsModal(facultyId);
  } else if (typeof openFacultyDetailsModal === 'function') {
    openFacultyDetailsModal(facultyId);
  } else {
    try {
      const res = await fetch(`/api/faculty/profile?faculty_id=${facultyId}`);
      const data = await res.json();
      if (data.success && data.faculty) {
        if (typeof renderFacultyDetails === 'function') renderFacultyDetails(data.faculty);
        const modal = document.getElementById('facultyDetailsModal');
        if (modal) modal.classList.add('open');
      }
    } catch (err) {
      console.error(err);
    }
  }
}
window.openViewFacultyDetailsModal = openViewFacultyDetailsModal;

// Global exposure
window.runAvailabilitySearch = runAvailabilitySearch;
window.debounceAvailabilitySearch = debounceAvailabilitySearch;
window.openUpdateAvailabilityModal = openUpdateAvailabilityModal;
window.openViewFacultyDetailsModal = openViewFacultyDetailsModal;

function initAvailabilityTracker() {
  runAvailabilitySearch();
}
window.initAvailabilityTracker = initAvailabilityTracker;
