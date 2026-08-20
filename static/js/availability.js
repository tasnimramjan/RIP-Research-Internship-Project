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
      if (res.status === 404) {
        container.style.display = 'block';
        container.innerHTML = `<div style="text-align:center; padding:3rem; color:red;">
          <strong>Error 404: Endpoint not found.</strong><br><br>
          Please restart your Python server (Ctrl+C and run <code>python3 main.py</code> again) so it can load the new Availability Tracker code!
        </div>`;
        emptyState.style.display = 'none';
        return;
      }
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
    emptyState.style.display = 'none';
  }
}

function renderAvailabilityResults(results) {
  const emptyState = document.getElementById('availabilityEmptyState');
  const container = document.getElementById('trackerContainer');
  
  if (!results || results.length === 0) {
    emptyState.style.display = 'block';
    container.style.display = 'none';
    return;
  }
  
  emptyState.style.display = 'none';
  container.style.display = 'grid';
  
  container.innerHTML = results.map(f => {
    // Determine badge colors based on status
    let badgeColor = '';
    let badgeBg = '';
    if (f.status === 'Available') {
      badgeColor = 'var(--accent-teal)';
      badgeBg = 'rgba(20,184,166,0.1)';
    } else if (f.status === 'Limited') {
      badgeColor = 'var(--accent-pink)';
      badgeBg = 'rgba(2ec,72,153,0.1)';
    } else {
      badgeColor = 'var(--text-muted)';
      badgeBg = 'var(--bg-lighter)';
    }
    
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
          <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; color:var(--text-main);">Research Interests:</div>
          <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
            ${f.research_domains.slice(0, 3).map(d => `<span class="badge" style="background:var(--bg-lighter); color:var(--text-main);">${d}</span>`).join('')}
            ${f.research_domains.length > 3 ? `<span class="badge" style="background:var(--bg-lighter); color:var(--text-muted);">+${f.research_domains.length - 3} more</span>` : ''}
          </div>
        </div>
        
        ${f.lab_name ? `
        <div style="font-size:0.8rem; margin-bottom:1rem; color:var(--text-muted);">
          <strong>Lab:</strong> ${f.lab_name}
        </div>
        ` : ''}
        
        <div style="background:var(--bg-main); border-radius:var(--radius); padding:0.8rem; display:flex; justify-content:space-between; text-align:center;">
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:var(--text-main);">${f.current_students}</div>
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Current</div>
          </div>
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:var(--text-main);">${f.max_capacity}</div>
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">Max Capacity</div>
          </div>
          <div>
            <div style="font-size:1.2rem; font-weight:800; color:${badgeColor};">${f.remaining_slots}</div>
            <div style="font-size:0.7rem; color:${badgeColor}; text-transform:uppercase; letter-spacing:0.5px;">Remaining</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Global exposure
window.runAvailabilitySearch = runAvailabilitySearch;
window.debounceAvailabilitySearch = debounceAvailabilitySearch;

function initAvailabilityTracker() {
  runAvailabilitySearch();
}
window.initAvailabilityTracker = initAvailabilityTracker;
