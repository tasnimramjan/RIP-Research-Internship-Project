let facultySearchTimeout = null;

function debounceFacultySearch() {
  clearTimeout(facultySearchTimeout);
  facultySearchTimeout = setTimeout(() => {
    runFacultySearch();
  }, 300);
}

async function runFacultySearch() {
  const keywords = document.getElementById('facultySearchInput').value;
  const department = document.getElementById('facultyDeptFilter').value;
  const domain = document.getElementById('facultyDomainFilter').value;
  const lab = document.getElementById('facultyLabFilter').value;
  
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
  list.innerHTML = '';
  
  if (!faculties || faculties.length === 0) {
    list.style.display = 'none';
    empty.style.display = 'block';
    return;
  }
  
  list.style.display = 'grid';
  empty.style.display = 'none';
  
  faculties.forEach(fac => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.cursor = 'pointer';
    card.onclick = () => openFacultyDetailsModal(fac.user_id);
    
    const domainsHtml = fac.research_domains.slice(0, 3).map(d => `<span class="badge" style="background:var(--accent-cyan); color:#000;">${d}</span>`).join('');
    const moreDomains = fac.research_domains.length > 3 ? `<span class="badge" style="background:var(--bg-lighter); color:var(--text-muted);">+${fac.research_domains.length - 3} more</span>` : '';
    
    card.innerHTML = `
      <h3 style="font-size:1.1rem; font-weight:800; color:var(--accent-pink); margin-bottom:0.2rem;">${fac.name}</h3>
      <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:1rem;">${fac.designation}, ${fac.department}</div>
      <div style="margin-bottom:0.8rem;">
        <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Expertise & Interests:</div>
        <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
          ${domainsHtml}${moreDomains}
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:0.8rem; margin-top:auto;">
        <span style="font-size:0.8rem; color:var(--text-muted);">h-index: <strong>${fac.h_index}</strong></span>
        <span style="font-size:0.8rem; color:var(--text-muted);">Labs: <strong>${fac.directed_labs.length}</strong></span>
        <span style="font-size:0.8rem; color:var(--text-muted);">Pubs: <strong>${fac.publications.length}</strong></span>
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
  
  document.getElementById('facDetailsHIndex').textContent = fac.h_index;
  document.getElementById('facDetailsSlots').textContent = fac.remaining_slots;
  document.getElementById('facDetailsCgpa').textContent = fac.min_cgpa_req;
  
  const domainsContainer = document.getElementById('facDetailsDomains');
  domainsContainer.innerHTML = fac.research_domains.map(d => `<span class="badge" style="background:var(--accent-cyan); color:#000;">${d}</span>`).join('');
  
  const labsContainer = document.getElementById('facDetailsLabs');
  if (fac.directed_labs && fac.directed_labs.length > 0) {
    labsContainer.innerHTML = fac.directed_labs.map(l => `
      <div style="background:var(--bg-card); padding:1rem; border-radius:var(--radius); border:1px solid var(--border-color); margin-bottom:0.8rem;">
        <h5 style="font-size:1rem; font-weight:700; color:var(--accent-pink); margin-bottom:0.3rem;">${l.lab_name}</h5>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem;"><strong>Focus:</strong> ${l.focus_area}</div>
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
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.3rem;"><strong>Authors:</strong> ${p.authors.join(', ')}</div>
        <div style="font-size:0.85rem; color:var(--text-muted);"><strong>Domain:</strong> ${p.domain} | <strong>Year:</strong> ${p.publication_year}</div>
      </div>
    `).join('');
  } else {
    pubsContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--text-muted);">No publications found.</p>';
  }

  // Edit Profile button visibility
  const editBtn = document.getElementById('editFacultyProfileBtn');
  if (window.currentUser && window.currentUser.user_id === fac.faculty_id) {
    editBtn.style.display = 'block';
    // Pre-fill modal
    document.getElementById('editFacDesignation').value = fac.designation || '';
    document.getElementById('editFacDomains').value = (fac.research_domains || []).join(', ');
    document.getElementById('editFacHIndex').value = fac.h_index || 0;
    document.getElementById('editFacSlots').value = fac.remaining_slots || 0;
    document.getElementById('editFacCgpa').value = fac.min_cgpa_req || 0.0;
    document.getElementById('editFacThesisAvail').checked = !!fac.thesis_available;
  } else {
    editBtn.style.display = 'none';
  }
}

async function submitEditFacultyProfile() {
  const designation = document.getElementById('editFacDesignation').value.trim();
  const domains = document.getElementById('editFacDomains').value.split(',').map(s => s.trim()).filter(Boolean);
  const hIndex = parseInt(document.getElementById('editFacHIndex').value) || 0;
  const slots = parseInt(document.getElementById('editFacSlots').value) || 0;
  const cgpa = parseFloat(document.getElementById('editFacCgpa').value) || 0.0;
  const thesisAvail = document.getElementById('editFacThesisAvail').checked ? 1 : 0;

  try {
    const res = await fetch('/api/faculty/update_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        faculty_id: window.currentUser.user_id,
        designation: designation,
        research_domains: domains,
        h_index: hIndex,
        remaining_slots: slots,
        min_cgpa_req: cgpa,
        thesis_available: thesisAvail
      })
    });
    const data = await res.json();
    if (data.success) {
      alert('Profile updated successfully!');
      document.getElementById('editFacultyProfileModal').classList.remove('open');
      runFacultySearch(); // refresh
      closeFacultyDetailsModal(); // close modal
    } else {
      alert(data.message || 'Error updating profile');
    }
  } catch (e) {
    console.error(e);
    alert('Error updating profile');
  }
}

// Ensure the function is exposed globally
window.runFacultySearch = runFacultySearch;
window.debounceFacultySearch = debounceFacultySearch;
window.openFacultyDetailsModal = openFacultyDetailsModal;
window.closeFacultyDetailsModal = closeFacultyDetailsModal;
window.submitEditFacultyProfile = submitEditFacultyProfile;

// Load initial data when entering this view
// We can hook into the switchView from app.js by using an interval or monkey-patching it,
// but for simplicity we will just load it on DOMContentLoaded or wait for the user to click.
// We'll load it immediately since the panel starts hidden.
document.addEventListener('DOMContentLoaded', () => {
    runFacultySearch();
});
