// ==========================================================
// Discussion Forums & Thread Reminders — Client Controller & View
// ==========================================================

const Forums = {
  currentUser: null,
  currentSpace: 'General Academic Discussions',
  spacesData: {
    accessible_spaces: ['General Academic Discussions'],
    all_spaces: ['Thesis', 'Projects', 'Internships', 'Defense Preparation', 'General Academic Discussions'],
    space_status: {},
    space_reasons: {},
    is_admin: false
  },
  threads: [],
  searchQuery: '',
  pollingInterval: null,
  activeReminderThread: null,
  activeReminderTitle: '',
  socket: null,
  audioChime: null,

  init(user) {
    this.currentUser = user || (window.currentUser || null);
    if (!this.currentUser) return;

    this.initSocket();
    this.initAudio();
    this.setupModalEvents();
    this.loadSpacesAndThreads();
    this.startReminderPolling();
  },

  initAudio() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    } catch (e) {
      console.warn("AudioContext not supported", e);
    }
  },

  playChime() {
    try {
      if (!this.audioCtx) return;
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, this.audioCtx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, this.audioCtx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.2, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.4);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.4);
    } catch (e) {
      // Audio autoplay restrictions fallback
    }
  },

  initSocket() {
    this.socket = {
      on: (event, callback) => {
        window.addEventListener('rip_socket_' + event, (e) => callback(e.detail));
      },
      emit: (event, data) => {
        window.dispatchEvent(new CustomEvent('rip_socket_' + event, { detail: data }));
      }
    };

    // Bind real-time thread reminder receiver
    this.socket.on('thread_reminder', (reminder) => {
      this.showReminderAlert(reminder);
    });

    this.socket.on('forum_thread_created', (data) => {
      if (data && data.category === this.currentSpace) {
        this.loadThreads(false);
      }
    });
  },

  setupModalEvents() {
    const openBtn = document.getElementById('openCreateThreadBtn');
    const modal = document.getElementById('createThreadModal');
    const form = document.getElementById('createThreadForm');

    if (openBtn) {
      openBtn.onclick = () => {
        if (!this.currentUser) return alert('Please log in to start a discussion thread.');
        this.populateCreateModalCategoryOptions();
        modal.classList.add('open');
      };
    }

    if (form) {
      form.onsubmit = async (e) => {
        e.preventDefault();
        const title = document.getElementById('threadTitle').value.trim();
        const category = document.getElementById('threadCategory').value;
        const content = document.getElementById('threadContent').value.trim();
        if (!title || !content) return alert('Title and content are required.');
        await this.createThread(title, category, content);
      };
    }

    // Reminder date and time live preview
    const dateInput = document.getElementById('reminderDateInput');
    const timeInput = document.getElementById('reminderTimeInput');
    const updatePreview = () => {
      const d = dateInput ? dateInput.value : '';
      const t = timeInput ? timeInput.value : '';
      const previewEl = document.getElementById('reminderLivePreview');
      if (!previewEl) return;
      if (!d || !t) {
        previewEl.innerHTML = 'Target: Please select a valid date and time';
        return;
      }
      const [year, month, day] = d.split('-');
      const formattedDate = `${day}/${month}/${year}`;
      const [hours, mins] = t.split(':');
      let hourNum = parseInt(hours, 10);
      const ampm = hourNum >= 12 ? 'PM' : 'AM';
      hourNum = hourNum % 12 || 12;
      const formattedTime = `${hourNum}:${mins} ${ampm}`;
      previewEl.innerHTML = `<strong>Scheduled for:</strong> ${formattedDate} at ${formattedTime}`;
    };

    if (dateInput) dateInput.addEventListener('input', updatePreview);
    if (timeInput) timeInput.addEventListener('input', updatePreview);
  },

  populateCreateModalCategoryOptions() {
    const select = document.getElementById('threadCategory');
    const notice = document.getElementById('threadCategoryNotice');
    if (!select) return;

    select.innerHTML = '';
    const allSpaces = this.spacesData.all_spaces || [
      'General Academic Discussions',
      'Thesis',
      'Projects',
      'Internships',
      'Defense Preparation'
    ];

    allSpaces.forEach(s => {
      const isAllowed = this.spacesData.is_admin || (this.spacesData.accessible_spaces && this.spacesData.accessible_spaces.includes(s));
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = isAllowed ? s : `${s} (Locked)`;
      opt.disabled = !isAllowed;
      if (s === this.currentSpace && isAllowed) opt.selected = true;
      select.appendChild(opt);
    });

    const updateNotice = () => {
      const val = select.value;
      const reason = this.spacesData.space_reasons ? this.spacesData.space_reasons[val] : '';
      if (notice) notice.textContent = reason || '';
    };

    select.onchange = updateNotice;
    updateNotice();
  },

  async loadSpacesAndThreads() {
    if (!this.currentUser) return;
    try {
      const res = await fetch(`/api/forums/spaces?user_id=${this.currentUser.user_id}`);
      const data = await res.json();
      if (data.success) {
        this.spacesData = data;
        // If current space is not accessible, default to first accessible space
        if (!data.is_admin && !data.accessible_spaces.includes(this.currentSpace)) {
          this.currentSpace = data.accessible_spaces[0] || 'General Academic Discussions';
        }
      }
    } catch (e) {
      console.error('Failed to load forum spaces', e);
    }

    this.renderContainerStructure();
    await this.loadThreads();

    if (this.spacesData.is_admin) {
      this.loadAdminStats();
    }
  },

  renderContainerStructure() {
    const root = document.getElementById('forums-app');
    if (!root) return;

    const allSpaces = this.spacesData.all_spaces || [
      'Thesis',
      'Projects',
      'Internships',
      'Defense Preparation',
      'General Academic Discussions'
    ];

    root.innerHTML = `
      <div class="forums-wrapper">
        ${this.spacesData.is_admin ? `
          <div id="forumAdminBanner" class="forum-admin-banner">
            <div class="forum-admin-header">
              <div class="forum-admin-title">
                <span>Discussion Space Moderation & Analytics</span>
              </div>
              <button class="btn btn-sm btn-secondary" onclick="Forums.openAdminRemindersModal()">Manage Reminders</button>
            </div>
            <div id="forumAdminStats" class="forum-admin-stats-grid">
              <div class="forum-stat-card"><div class="forum-stat-num" id="statTotalThreads">-</div><div class="forum-stat-label">Threads</div></div>
              <div class="forum-stat-card"><div class="forum-stat-num" id="statTotalComments">-</div><div class="forum-stat-label">Comments</div></div>
              <div class="forum-stat-card"><div class="forum-stat-num" id="statTotalReactions">-</div><div class="forum-stat-label">Reactions</div></div>
              <div class="forum-stat-card"><div class="forum-stat-num" id="statActiveReminders">-</div><div class="forum-stat-label">Active Reminders</div></div>
            </div>
          </div>
        ` : ''}

        <div class="forums-main-layout">
          <!-- Sidebar: Dedicated Discussion Spaces -->
          <div class="forums-sidebar">
            <div class="forums-sidebar-title">
              <span>Discussion Spaces</span>
              <span style="font-size:0.75rem; color:var(--accent-cyan);">${this.currentUser.role}</span>
            </div>
            <ul class="space-nav-list" id="spaceNavList">
              ${allSpaces.map(s => {
                const isAccessible = this.spacesData.is_admin || (this.spacesData.accessible_spaces && this.spacesData.accessible_spaces.includes(s));
                const isActive = (s === this.currentSpace);

                return `
                  <li class="space-nav-item ${isActive ? 'active' : ''} ${!isAccessible ? 'locked' : ''}" 
                      onclick="Forums.selectSpace('${s}')" title="${this.spacesData.space_reasons ? (this.spacesData.space_reasons[s] || '') : ''}">
                    <div class="space-item-label">
                      <span>${s}</span>
                    </div>
                    <div>
                      ${!isAccessible ? '<span class="space-locked-pill">Locked</span>' : '<span class="space-active-pill">Active</span>'}
                    </div>
                  </li>
                `;
              }).join('')}
            </ul>
          </div>

          <!-- Content: Threads & Toolbar -->
          <div class="forums-content">
            <div class="forums-toolbar">
              <div class="forums-search-box">
                <input type="text" id="forumSearchInput" placeholder="Search discussions in ${this.currentSpace}..." oninput="Forums.handleSearch(this.value)" style="padding-left:1rem;">
              </div>
              <div style="display:flex; gap:0.5rem; align-items:center;">
                <span style="font-size:0.85rem; color:var(--text-muted);">Current Space:</span>
                <span class="space-badge space-${this.currentSpace.replace(/\s+/g, '-')}">${this.currentSpace}</span>
              </div>
            </div>

            <!-- Inaccessible Space Warning -->
            <div id="lockedSpaceBanner" style="display:none;" class="locked-space-notice">
              <h3>Space Access Restricted</h3>
              <p id="lockedSpaceReasonText"></p>
              <div id="lockedSpaceActionBtn"></div>
            </div>

            <!-- Threads List -->
            <div id="threadsContainer" class="threads-container">
              <div style="text-align:center; padding:2rem; color:var(--text-muted);">Loading discussions...</div>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  async loadAdminStats() {
    if (!this.spacesData.is_admin) return;
    try {
      const res = await fetch(`/api/forums/admin/stats?user_id=${this.currentUser.user_id}`);
      const data = await res.json();
      if (data.success && data.stats) {
        document.getElementById('statTotalThreads').innerText = data.stats.total_threads || 0;
        document.getElementById('statTotalComments').innerText = data.stats.total_comments || 0;
        document.getElementById('statTotalReactions').innerText = data.stats.total_reactions || 0;
        document.getElementById('statActiveReminders').innerText = data.stats.active_reminders || 0;
      }
    } catch (e) {
      console.error('Failed to load admin forum stats', e);
    }
  },

  selectSpace(spaceName) {
    this.currentSpace = spaceName;
    this.renderContainerStructure();
    this.loadThreads();
  },

  handleSearch(query) {
    this.searchQuery = (query || '').toLowerCase().trim();
    this.renderThreadsList();
  },

  async loadThreads(showLoader = true) {
    const isAccessible = this.spacesData.is_admin || (this.spacesData.accessible_spaces && this.spacesData.accessible_spaces.includes(this.currentSpace));
    const lockedBanner = document.getElementById('lockedSpaceBanner');
    const container = document.getElementById('threadsContainer');

    if (!isAccessible) {
      if (lockedBanner) {
        lockedBanner.style.display = 'flex';
        const reason = (this.spacesData.space_reasons && this.spacesData.space_reasons[this.currentSpace]) || 'You do not have active participation in this discussion space.';
        document.getElementById('lockedSpaceReasonText').innerText = reason;
        
        const actionBtn = document.getElementById('lockedSpaceActionBtn');
        if (this.currentSpace === 'Thesis') {
          actionBtn.innerHTML = `<button class="btn btn-sm btn-cyan" onclick="switchView('thesis-groups')">Explore Thesis Groups</button>`;
        } else if (this.currentSpace === 'Projects') {
          actionBtn.innerHTML = `<button class="btn btn-sm btn-cyan" onclick="switchView('teammate-finder')">Explore Project Teammates</button>`;
        } else if (this.currentSpace === 'Internships') {
          actionBtn.innerHTML = `<button class="btn btn-sm btn-cyan" onclick="switchView('internship-portal')">View Internship Portal</button>`;
        } else {
          actionBtn.innerHTML = '';
        }
      }
      if (container) container.innerHTML = '';
      return;
    } else {
      if (lockedBanner) lockedBanner.style.display = 'none';
    }

    if (showLoader && container) {
      container.innerHTML = '<div style="text-align:center; padding:2rem; color:var(--text-muted);">Loading discussions...</div>';
    }

    try {
      const url = `/api/forums/threads?category=${encodeURIComponent(this.currentSpace)}&user_id=${this.currentUser.user_id}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) {
        this.threads = data.threads || [];
        this.renderThreadsList();
      }
    } catch (e) {
      console.error('Failed to load threads', e);
      if (container) container.innerHTML = '<p style="color:#ef4444; text-align:center; padding:1.5rem;">Failed to load threads. Please try again.</p>';
    }
  },

  renderThreadsList() {
    const container = document.getElementById('threadsContainer');
    if (!container) return;

    let list = this.threads;
    if (this.searchQuery) {
      list = list.filter(t => 
        (t.title && t.title.toLowerCase().includes(this.searchQuery)) ||
        (t.content && t.content.toLowerCase().includes(this.searchQuery)) ||
        (t.author_name && t.author_name.toLowerCase().includes(this.searchQuery))
      );
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="background:var(--bg-card); border:1px dashed var(--border-color); border-radius:var(--radius); padding:3rem; text-align:center;">
          <p style="font-size:1.1rem; color:var(--text-muted); margin-bottom:0.8rem;">No discussion threads found in <strong>${this.currentSpace}</strong>.</p>
          <button class="btn btn-sm btn-cyan" onclick="document.getElementById('openCreateThreadBtn').click()">+ Start the First Discussion</button>
        </div>
      `;
      return;
    }

    container.innerHTML = list.map(t => {
      const likeCount = (t.reactions && t.reactions.like) ? t.reactions.like : 0;
      const commentsCount = (t.comments && t.comments.length) ? t.comments.length : 0;
      const userReacted = Boolean(t.user_reacted);
      const hasReminder = Boolean(t.user_reminder);

      return `
        <div class="thread-card" id="thread-card-${t.thread_id}">
          <div class="thread-header">
            <div class="thread-meta-left">
              <span class="space-badge space-${(t.category || '').replace(/\s+/g, '-')}">${t.category}</span>
              <span class="thread-author-chip">Posted by <strong>${t.author_name}</strong> &bull; <span class="role-pill role-${t.author_role}">${t.author_role}</span> (${t.department})</span>
              <span class="thread-timestamp">&bull; ${this.formatDateTime(t.created_at)}</span>
            </div>
            ${t.can_delete ? `
              <button class="btn btn-sm btn-danger" style="padding:0.25rem 0.6rem; font-size:0.75rem;" onclick="Forums.deleteThread('${t.thread_id}')">
                Delete
              </button>
            ` : ''}
          </div>

          <h3 class="thread-title">${this.escapeHtml(t.title)}</h3>
          <div class="thread-body">${this.escapeHtml(t.content)}</div>

          <div class="thread-actions-bar">
            <div class="thread-actions-left">
              <button class="btn-forum-action ${userReacted ? 'reacted' : ''}" onclick="Forums.toggleReaction('${t.thread_id}')">
                <span>❤️</span>
                <span>${likeCount} ${likeCount === 1 ? 'Reaction' : 'Reactions'}</span>
              </button>

              <button class="btn-forum-action" onclick="Forums.toggleComments('${t.thread_id}')">
                <span>💬</span>
                <span>${commentsCount} ${commentsCount === 1 ? 'Comment' : 'Comments'}</span>
              </button>

              <button class="btn-forum-action ${hasReminder ? 'reminded' : ''}" onclick="Forums.promptReminder('${t.thread_id}', '${this.escapeJs(t.title)}')">
                <span>⏰</span>
                <span>${hasReminder ? `Reminder set: ${this.formatDateTime(t.user_reminder.remind_at)}` : 'Remind Me'}</span>
              </button>
            </div>

            ${this.spacesData.is_admin ? `
              <button class="btn-forum-action" style="color:var(--accent-pink);" onclick="Forums.moderateReactions('${t.thread_id}')">
                Moderate Reactions
              </button>
            ` : ''}
          </div>

          <!-- Comments Accordion -->
          <div class="comments-accordion" id="comments-${t.thread_id}">
            <div class="comments-list">
              ${(t.comments && t.comments.length > 0) ? t.comments.map(c => `
                <div class="comment-card" id="comment-${c.comment_id}">
                  <div class="comment-meta">
                    <span class="comment-author">
                      <strong>${this.escapeHtml(c.author_name)}</strong> 
                      <span class="role-pill role-${c.author_role}" style="font-size:0.68rem; padding:0.1rem 0.4rem;">${c.author_role}</span>
                      &bull; <span style="font-size:0.72rem; color:var(--text-muted);">${this.formatDateTime(c.created_at)}</span>
                    </span>
                    ${c.can_delete ? `
                      <button class="btn btn-sm btn-danger" style="padding:0.15rem 0.45rem; font-size:0.7rem;" onclick="Forums.deleteComment('${c.comment_id}')">Delete</button>
                    ` : ''}
                  </div>
                  <div class="comment-text">${this.escapeHtml(c.content)}</div>
                  <div class="comment-actions">
                    <button class="btn-forum-action ${c.user_reacted ? 'reacted' : ''}" style="padding:0.2rem 0.5rem; font-size:0.75rem;" onclick="Forums.toggleCommentReaction('${c.comment_id}')">
                      ❤️ <span>${(c.reactions && c.reactions.like) || 0}</span>
                    </button>
                  </div>
                </div>
              `).join('') : '<p style="color:var(--text-muted); font-size:0.85rem; padding:0.5rem 0;">No comments yet. Be the first to reply!</p>'}
            </div>

            <div class="comment-input-bar">
              <input type="text" id="comment-input-${t.thread_id}" placeholder="Write a comment..." onkeypress="if(event.key==='Enter') Forums.postComment('${t.thread_id}')">
              <button class="btn btn-sm btn-cyan" onclick="Forums.postComment('${t.thread_id}')">Post</button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  toggleComments(threadId) {
    const el = document.getElementById(`comments-${threadId}`);
    if (el) {
      el.classList.toggle('open');
    }
  },

  async createThread(title, category, content) {
    try {
      const res = await fetch('/api/forums/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          title,
          category,
          content
        })
      });
      const data = await res.json();
      if (data.success) {
        document.getElementById('createThreadModal').classList.remove('open');
        document.getElementById('createThreadForm').reset();
        this.currentSpace = category;
        this.renderContainerStructure();
        await this.loadThreads();
        if (this.socket) {
          this.socket.emit('forum_thread_created', { category });
        }
      } else {
        alert(data.message || 'Failed to create thread.');
      }
    } catch (e) {
      console.error('Thread creation error', e);
    }
  },

  async postComment(threadId) {
    const input = document.getElementById(`comment-input-${threadId}`);
    if (!input) return;
    const content = input.value.trim();
    if (!content) return;

    try {
      const res = await fetch('/api/forums/comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          thread_id: threadId,
          content
        })
      });
      const data = await res.json();
      if (data.success) {
        input.value = '';
        await this.loadThreads(false);
        const sec = document.getElementById(`comments-${threadId}`);
        if (sec) sec.classList.add('open');
      } else {
        alert(data.message || 'Failed to post comment.');
      }
    } catch (e) {
      console.error('Comment posting error', e);
    }
  },

  async deleteComment(commentId) {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    try {
      const res = await fetch('/api/forums/comment/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          comment_id: commentId
        })
      });
      const data = await res.json();
      if (data.success) {
        await this.loadThreads(false);
      } else {
        alert(data.message || 'Failed to delete comment.');
      }
    } catch (e) {
      console.error('Delete comment error', e);
    }
  },

  async toggleReaction(threadId) {
    try {
      const res = await fetch('/api/forums/react', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          thread_id: threadId,
          reaction_type: 'like'
        })
      });
      const data = await res.json();
      if (data.success) {
        await this.loadThreads(false);
      } else {
        alert(data.message || 'Reaction failed.');
      }
    } catch (e) {
      console.error('Reaction toggle error', e);
    }
  },

  async toggleCommentReaction(commentId) {
    try {
      const res = await fetch('/api/forums/react', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          comment_id: commentId,
          reaction_type: 'like'
        })
      });
      const data = await res.json();
      if (data.success) {
        await this.loadThreads(false);
      }
    } catch (e) {
      console.error('Comment reaction error', e);
    }
  },

  async moderateReactions(threadId) {
    if (!confirm('Admin: Clear all reactions for this thread?')) return;
    try {
      const res = await fetch('/api/forums/react/moderate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          thread_id: threadId
        })
      });
      const data = await res.json();
      alert(data.message);
      if (data.success) {
        await this.loadThreads(false);
      }
    } catch (e) {
      console.error('Moderation error', e);
    }
  },

  async deleteThread(threadId) {
    if (!confirm('Are you sure you want to delete this discussion thread?')) return;
    try {
      const res = await fetch('/api/forums/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          thread_id: threadId
        })
      });
      const data = await res.json();
      alert(data.message);
      if (data.success) {
        await this.loadThreads();
        if (this.spacesData.is_admin) this.loadAdminStats();
      }
    } catch (e) {
      console.error('Delete thread error', e);
    }
  },

  promptReminder(threadId, threadTitle) {
    this.activeReminderThread = threadId;
    this.activeReminderTitle = threadTitle;

    const titleEl = document.getElementById('reminderThreadTitle');
    if (titleEl) titleEl.innerText = `Thread: "${threadTitle}"`;

    // Default to 1 hour from now formatted
    const now = new Date();
    now.setHours(now.getHours() + 1);

    const pad = n => (n < 10 ? '0' + n : n);
    const dateVal = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const timeVal = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

    const dateInput = document.getElementById('reminderDateInput');
    const timeInput = document.getElementById('reminderTimeInput');
    const noteInput = document.getElementById('reminderNote');

    if (dateInput) dateInput.value = dateVal;
    if (timeInput) timeInput.value = timeVal;
    if (noteInput) noteInput.value = '';

    const previewEl = document.getElementById('reminderLivePreview');
    if (previewEl) {
      const [year, month, day] = dateVal.split('-');
      const [h, m] = timeVal.split(':');
      let hNum = parseInt(h, 10);
      const ampm = hNum >= 12 ? 'PM' : 'AM';
      hNum = hNum % 12 || 12;
      previewEl.innerHTML = `<strong>Scheduled for:</strong> ${day}/${month}/${year} at ${hNum}:${m} ${ampm}`;
    }

    document.getElementById('setReminderModal').classList.add('open');
  },

  async submitReminder() {
    const dateVal = document.getElementById('reminderDateInput').value;
    const timeVal = document.getElementById('reminderTimeInput').value;
    const note = document.getElementById('reminderNote').value.trim();

    if (!dateVal || !timeVal) {
      return alert('Please select both a date and time for the reminder.');
    }

    const remind_at = `${dateVal} ${timeVal}:00`;

    try {
      const res = await fetch('/api/forums/reminder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          thread_id: this.activeReminderThread,
          remind_at,
          note: note || `Reminder for "${this.activeReminderTitle}"`
        })
      });
      const data = await res.json();
      if (data.success) {
        document.getElementById('setReminderModal').classList.remove('open');
        this.showToastNotification(`Reminder set for ${remind_at}!`);
        await this.loadThreads(false);

        // Notify real-time socket layer
        if (this.socket) {
          this.socket.emit('reminder_scheduled', {
            reminder_id: data.reminder_id,
            remind_at,
            thread_id: this.activeReminderThread
          });
        }
      } else {
        alert(data.message || 'Failed to schedule reminder.');
      }
    } catch (e) {
      console.error('Reminder error', e);
    }
  },

  startReminderPolling() {
    if (this.pollingInterval) clearInterval(this.pollingInterval);

    // Poll every 6 seconds for due reminders in SQLite
    this.pollingInterval = setInterval(async () => {
      if (!this.currentUser) return;
      try {
        const res = await fetch(`/api/forums/reminders?user_id=${this.currentUser.user_id}`);
        const data = await res.json();
        if (data.success && data.reminders && data.reminders.length > 0) {
          data.reminders.forEach(r => {
            if (this.socket) {
              this.socket.emit('thread_reminder', r);
            } else {
              this.showReminderAlert(r);
            }
          });
        }
      } catch (e) {
        // network polling silent catch
      }
    }, 6000);
  },

  showReminderAlert(reminder) {
    this.playChime();

    // Check if duplicate toast already on screen
    const existing = document.getElementById(`reminder-toast-${reminder.reminder_id}`);
    if (existing) return;

    const toast = document.createElement('div');
    toast.className = 'reminder-toast-alert';
    toast.id = `reminder-toast-${reminder.reminder_id}`;
    toast.innerHTML = `
      <div class="reminder-toast-header">
        <span class="reminder-toast-title">Thread Reminder Alert</span>
        <button style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.1rem;" onclick="this.closest('.reminder-toast-alert').remove()">&times;</button>
      </div>
      <div class="reminder-toast-body">
        <strong>${this.escapeHtml(reminder.thread_title || 'Discussion Thread')}</strong>
        <div style="font-size:0.78rem; color:var(--accent-cyan); margin-top:0.2rem;">Space: ${reminder.category || 'Discussion'}</div>
      </div>
      ${reminder.note ? `<div class="reminder-toast-note">Note: ${this.escapeHtml(reminder.note)}</div>` : ''}
      <div class="reminder-toast-actions">
        <button class="btn btn-sm btn-secondary" onclick="this.closest('.reminder-toast-alert').remove()">Dismiss</button>
        <button class="btn btn-sm btn-cyan" onclick="Forums.goToReminderThread('${reminder.category || ''}', '${reminder.thread_id}', '${reminder.reminder_id}')">Open Thread</button>
      </div>
    `;

    document.body.appendChild(toast);

    // Auto-remove toast after 30 seconds
    setTimeout(() => {
      if (document.body.contains(toast)) toast.remove();
    }, 30000);
  },

  goToReminderThread(category, threadId, toastId) {
    if (toastId) {
      const t = document.getElementById(`reminder-toast-${toastId}`);
      if (t) t.remove();
    }

    if (window.switchView) {
      window.switchView('discussion-forums');
    }

    if (category && category !== this.currentSpace) {
      this.selectSpace(category);
    }

    setTimeout(() => {
      const card = document.getElementById(`thread-card-${threadId}`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.style.borderColor = '#fbbf24';
        card.style.boxShadow = '0 0 20px rgba(245, 158, 11, 0.4)';
        setTimeout(() => {
          card.style.borderColor = '';
          card.style.boxShadow = '';
        }, 4000);
      }
    }, 300);
  },

  async openAdminRemindersModal() {
    if (!this.spacesData.is_admin) return;
    try {
      const res = await fetch(`/api/forums/admin/reminders?user_id=${this.currentUser.user_id}`);
      const data = await res.json();
      if (!data.success) return alert(data.message);

      const reminders = data.reminders || [];
      const modalHtml = `
        <div id="adminRemindersModal" class="modal-overlay open" style="z-index:9999;">
          <div class="modal-box" style="max-width: 680px; max-height: 80vh; overflow-y: auto;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
              <h3 style="font-size:1.2rem; font-weight:700; color:var(--accent-pink);">System Discussion Reminders</h3>
              <button class="btn btn-sm btn-secondary" onclick="document.getElementById('adminRemindersModal').remove()">&times; Close</button>
            </div>
            ${reminders.length === 0 ? '<p style="color:var(--text-muted);">No thread reminders in the system.</p>' : `
              <div style="display:flex; flex-direction:column; gap:0.6rem;">
                ${reminders.map(r => `
                  <div style="background:var(--bg-dark); border:1px solid var(--border-color); border-radius:8px; padding:0.8rem; display:flex; justify-content:space-between; align-items:center; gap:0.6rem;">
                    <div>
                      <div style="font-weight:600; font-size:0.9rem; color:#fff;">${this.escapeHtml(r.thread_title)}</div>
                      <div style="font-size:0.75rem; color:var(--text-muted);">User: ${r.user_name} (${r.user_email}) &bull; Target: ${r.remind_at}</div>
                      ${r.note ? `<div style="font-size:0.75rem; color:#fbbf24;">Note: ${this.escapeHtml(r.note)}</div>` : ''}
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="Forums.adminDeleteReminder('${r.reminder_id}')">Cancel</button>
                  </div>
                `).join('')}
              </div>
            `}
          </div>
        </div>
      `;

      const existing = document.getElementById('adminRemindersModal');
      if (existing) existing.remove();
      const div = document.createElement('div');
      div.innerHTML = modalHtml;
      document.body.appendChild(div.firstElementChild);
    } catch (e) {
      console.error('Failed to load admin reminders', e);
    }
  },

  async adminDeleteReminder(reminderId) {
    if (!confirm('Cancel this reminder?')) return;
    try {
      const res = await fetch('/api/forums/reminder/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.currentUser.user_id,
          reminder_id: reminderId
        })
      });
      const data = await res.json();
      alert(data.message);
      const m = document.getElementById('adminRemindersModal');
      if (m) m.remove();
      this.openAdminRemindersModal();
      this.loadAdminStats();
    } catch (e) {
      console.error('Delete reminder error', e);
    }
  },

  showToastNotification(msg) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(6, 182, 212, 0.95);
      color: #0f172a;
      font-weight: 700;
      padding: 0.8rem 1.4rem;
      border-radius: 999px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
      z-index: 9999;
      font-size: 0.9rem;
    `;
    toast.innerText = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
      if (document.body.contains(toast)) toast.remove();
    }, 3500);
  },

  formatDateTime(dtStr) {
    if (!dtStr) return '';
    try {
      const d = new Date(dtStr.replace(' ', 'T'));
      if (isNaN(d.getTime())) return dtStr;
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      });
    } catch (e) {
      return dtStr;
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  escapeJs(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
  }
};

window.Forums = Forums;
