// ==========================================================
// Discussion Forums & Thread Reminders (Role & Activity Aware)
// Dedicated Spaces:
// 1. Thesis (Relevant to Thesis activity/role)
// 2. Projects (Relevant to Project activity/role)
// 3. Internships (Relevant to Internship activity/role)
// 4. Defense Preparation (Relevant to Defense activity/role)
// 5. General Academic Discussions (Open to all registered users)
// ==========================================================

window.Forums = {
    currentUser: null,
    currentSpace: 'All',
    spacesAccess: {},
    pollingInterval: null,
    activeReminderThreadId: null,

    spaces: [
        { id: 'All', name: 'All Accessible', desc: 'Browse discussions across all accessible spaces.' },
        { id: 'Thesis', name: 'Thesis', desc: 'Dedicated space for thesis proposals, literature reviews, and research methodology.' },
        { id: 'Projects', name: 'Projects', desc: 'Dedicated space for capstone projects, software development, and technical collaboration.' },
        { id: 'Internships', name: 'Internships', desc: 'Dedicated space for industrial internships, placement tips, and job experiences.' },
        { id: 'Defense Preparation', name: 'Defense Preparation', desc: 'Dedicated space for presentation slides, defense questions, and panel preparation.' },
        { id: 'General Academic Discussions', name: 'General Academic Discussions', desc: 'Open discussion space for general academic queries and university announcements.' }
    ],

    getUser() {
        this.currentUser = window.currentUser || (typeof currentUser !== 'undefined' ? currentUser : null) || JSON.parse(localStorage.getItem('rip_user') || 'null');
        return this.currentUser;
    },

    async fetchSpacesAccess() {
        const user = this.getUser();
        if (!user) {
            this.spacesAccess = {
                "Thesis": false,
                "Projects": false,
                "Internships": false,
                "Defense Preparation": false,
                "General Academic Discussions": true
            };
            return this.spacesAccess;
        }

        try {
            const res = await fetch(`/api/forums/access?user_id=${user.user_id}`);
            const data = await res.json();
            if (data.success && data.access) {
                this.spacesAccess = data.access;
            }
        } catch (e) {
            console.error('Error fetching forum spaces access', e);
        }
        return this.spacesAccess;
    },

    hasSpaceAccess(spaceId) {
        if (spaceId === 'All' || spaceId === 'General Academic Discussions') return true;
        const user = this.getUser();
        if (!user) return false;
        if (user.role === 'Admin') return true;
        return !!this.spacesAccess[spaceId];
    },

    async init(user) {
        if (user) this.currentUser = user;
        else this.getUser();

        await this.fetchSpacesAccess();
        this.renderSpacesSidebar();
        this.loadThreads();
        this.startReminderPolling();
    },

    renderSpacesSidebar() {
        const listEl = document.getElementById('forumSpacesList');
        if (!listEl) return;

        listEl.innerHTML = this.spaces.map(s => {
            const hasAccess = this.hasSpaceAccess(s.id);
            const isActive = this.currentSpace === s.id;
            const badgeHtml = s.id === 'All' ? '' : (hasAccess 
                ? `<span class="space-active-pill">Active</span>` 
                : `<span class="space-locked-pill">Locked</span>`);

            return `
                <li class="forum-space-item ${isActive ? 'active' : ''}" onclick="Forums.selectSpace('${s.id}')">
                    <span>${s.name}</span>
                    ${badgeHtml}
                </li>
            `;
        }).join('');
    },

    selectSpace(spaceId) {
        this.currentSpace = spaceId;
        this.renderSpacesSidebar();
        
        const spaceObj = this.spaces.find(s => s.id === spaceId) || this.spaces[0];
        const titleEl = document.getElementById('currentSpaceTitle');
        const descEl = document.getElementById('currentSpaceDesc');
        const badgeEl = document.getElementById('currentSpaceAccessBadge');
        const newThreadBtn = document.getElementById('openCreateThreadBtn');

        if (titleEl) titleEl.innerText = spaceObj.name;
        if (descEl) descEl.innerText = spaceObj.desc;

        const hasAccess = this.hasSpaceAccess(spaceId);
        if (badgeEl) {
            if (spaceId === 'All') {
                badgeEl.innerHTML = '';
            } else if (hasAccess) {
                badgeEl.innerHTML = `<span class="space-active-pill">Active Space</span>`;
            } else {
                badgeEl.innerHTML = `<span class="space-locked-pill">Locked Space</span>`;
            }
        }

        if (newThreadBtn) {
            newThreadBtn.style.display = hasAccess ? 'inline-block' : 'none';
        }

        this.loadThreads();
    },

    async loadThreads() {
        const container = document.getElementById('threadsContainer');
        if (!container) return;

        const user = this.getUser();
        const hasAccess = this.hasSpaceAccess(this.currentSpace);

        if (!hasAccess) {
            container.innerHTML = `
                <div style="background:var(--bg-card); border:1px solid rgba(239,68,68,0.3); border-radius:var(--radius); padding:2.5rem; text-align:center;">
                    <h4 style="color:#ef4444; margin-bottom:0.5rem; font-size:1.1rem;">Discussion Space Locked</h4>
                    <p style="color:var(--text-muted); font-size:0.95rem; max-width:540px; margin:0 auto 1.2rem; line-height:1.6;">
                        Access to ${this.currentSpace} is restricted. Students and faculty can see their respective discussion space.
                    </p>
                    <button class="btn btn-sm btn-secondary" onclick="Forums.selectSpace('General Academic Discussions')">
                        Go to General Academic Discussions
                    </button>
                </div>
            `;
            return;
        }

        try {
            const url = (this.currentSpace === 'All')
                ? '/api/forums/threads'
                : `/api/forums/threads?category=${encodeURIComponent(this.currentSpace)}`;

            const res = await fetch(url);
            const data = await res.json();

            if (!data.success || !data.threads || data.threads.length === 0) {
                container.innerHTML = `
                    <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius); padding:3rem 1.5rem; text-align:center;">
                        <p style="color:var(--text-muted); font-size:0.95rem; margin-bottom:1rem;">No discussion threads found in this space.</p>
                        ${hasAccess ? `<button class="btn btn-sm btn-cyan" onclick="Forums.openCreateModal()">+ Start First Thread</button>` : ''}
                    </div>
                `;
                return;
            }

            // Filter out any threads from spaces the user has no access to when on 'All'
            const visibleThreads = data.threads.filter(t => this.hasSpaceAccess(t.category));

            if (visibleThreads.length === 0) {
                container.innerHTML = `
                    <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius); padding:3rem 1.5rem; text-align:center;">
                        <p style="color:var(--text-muted); font-size:0.95rem; margin-bottom:1rem;">No threads found in your accessible spaces.</p>
                        <button class="btn btn-sm btn-cyan" onclick="Forums.openCreateModal()">+ Start First Thread</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = visibleThreads.map(t => {
                const likeCount = (t.reactions && t.reactions.like) ? t.reactions.like : 0;
                const commentsCount = (t.comments && Array.isArray(t.comments)) ? t.comments.length : 0;
                const isAuthorOrAdmin = user && (user.user_id === t.user_id || user.role === 'Admin');

                return `
                    <div class="thread-card" id="thread-${t.thread_id}">
                        <div class="thread-meta">
                            <span class="badge">${this.escapeHtml(t.category)}</span>
                            <span>Posted by <strong>${this.escapeHtml(t.author_name)}</strong> (${this.escapeHtml(t.author_role || 'Member')})</span>
                            <span style="margin-left:auto;">${t.created_at ? t.created_at : ''}</span>
                        </div>
                        <div class="thread-title">${this.escapeHtml(t.title)}</div>
                        <div class="thread-content">${this.escapeHtml(t.content)}</div>

                        <div class="thread-actions">
                            <button class="forum-action-btn" onclick="Forums.reactToThread('${t.thread_id}')">
                                Like (${likeCount})
                            </button>
                            <button class="forum-action-btn" onclick="Forums.toggleComments('${t.thread_id}')">
                                Comments (${commentsCount})
                            </button>
                            <button class="forum-action-btn" onclick="Forums.openReminderModal('${t.thread_id}')">
                                Remind Me
                            </button>
                            ${isAuthorOrAdmin ? `
                                <button class="btn btn-sm btn-danger" style="margin-left:auto; padding:0.25rem 0.65rem; font-size:0.75rem;" onclick="Forums.deleteThread('${t.thread_id}')">
                                    Delete
                                </button>
                            ` : ''}
                        </div>

                        <div class="comments-section" id="comments-${t.thread_id}">
                            <div class="comments-list">
                                ${(t.comments && t.comments.length > 0) ? t.comments.map(c => `
                                    <div class="comment-item">
                                        <div class="comment-meta">
                                            <strong>${this.escapeHtml(c.author_name)}</strong> (${this.escapeHtml(c.author_role || 'Member')}) &bull; ${c.created_at ? c.created_at : ''}
                                        </div>
                                        <div class="comment-content">${this.escapeHtml(c.content)}</div>
                                    </div>
                                `).join('') : `<p style="color:var(--text-muted); font-size:0.85rem; padding:0.5rem 0;">No comments yet. Be the first to share your thoughts!</p>`}
                            </div>
                            <div class="comment-input-row">
                                <input type="text" id="comment-input-${t.thread_id}" placeholder="Write a comment...">
                                <button class="btn btn-sm btn-cyan" onclick="Forums.postComment('${t.thread_id}')">Post</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            console.error('Error loading threads', err);
            container.innerHTML = `<p style="color:var(--accent-pink); padding:2rem; text-align:center;">Failed to load discussions. Please refresh.</p>`;
        }
    },

    toggleComments(threadId) {
        const sec = document.getElementById(`comments-${threadId}`);
        if (sec) sec.classList.toggle('open');
    },

    // ── Create Thread Modal ──
    openCreateModal() {
        const user = this.getUser();
        if (!user) return alert('Please log in to create a discussion thread.');

        const modal = document.getElementById('createThreadModal');
        const catSelect = document.getElementById('threadCategory');
        if (!modal || !catSelect) return;

        // Populate only spaces the user has verified access to
        const allowed = this.spaces.filter(s => s.id !== 'All' && this.hasSpaceAccess(s.id));
        catSelect.innerHTML = allowed.map(s => `
            <option value="${s.id}" ${s.id === this.currentSpace ? 'selected' : ''}>${s.name}</option>
        `).join('');

        modal.classList.add('open');
    },

    closeCreateModal() {
        const modal = document.getElementById('createThreadModal');
        if (modal) modal.classList.remove('open');
        document.getElementById('createThreadForm')?.reset();
    },

    async handleCreateThread(e) {
        e.preventDefault();
        const user = this.getUser();
        if (!user) return alert('Please log in.');

        const title = document.getElementById('threadTitle').value.trim();
        const category = document.getElementById('threadCategory').value;
        const content = document.getElementById('threadContent').value.trim();

        if (!title || !category || !content) return alert('All fields are required.');

        try {
            const res = await fetch('/api/forums/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    title: title,
                    category: category,
                    content: content
                })
            });
            const data = await res.json();
            if (data.success) {
                this.closeCreateModal();
                this.currentSpace = category;
                this.renderSpacesSidebar();
                this.loadThreads();
            } else {
                alert(data.message || 'Failed to create thread.');
            }
        } catch (err) {
            console.error('Create thread error', err);
        }
    },

    async postComment(threadId) {
        const user = this.getUser();
        if (!user) return alert('Please log in to comment.');

        const input = document.getElementById(`comment-input-${threadId}`);
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;

        input.value = '';

        try {
            const res = await fetch('/api/forums/comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    thread_id: threadId,
                    content: text
                })
            });
            const data = await res.json();
            if (data.success) {
                this.loadThreads();
            } else {
                alert(data.message || 'Failed to post comment.');
            }
        } catch (err) {
            console.error('Post comment error', err);
        }
    },

    async reactToThread(threadId) {
        const user = this.getUser();
        if (!user) return alert('Please log in to react.');

        try {
            const res = await fetch('/api/forums/react', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    thread_id: threadId,
                    reaction_type: 'like'
                })
            });
            const data = await res.json();
            if (data.success) {
                this.loadThreads();
            }
        } catch (err) {
            console.error('Reaction error', err);
        }
    },

    async deleteThread(threadId) {
        const user = this.getUser();
        if (!user) return alert('Please log in.');
        if (!confirm('Are you sure you want to delete this discussion thread?')) return;

        try {
            const res = await fetch('/api/forums/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    thread_id: threadId
                })
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                this.loadThreads();
            }
        } catch (err) {
            console.error('Delete thread error', err);
        }
    },

    // ── Reminder Modal with Specific Date & Time Selection ──
    openReminderModal(threadId) {
        const user = this.getUser();
        if (!user) return alert('Please log in to set a thread reminder.');

        this.activeReminderThreadId = threadId;
        const modal = document.getElementById('setReminderModal');
        if (!modal) return;

        // Set default date & time (1 hour from now)
        const now = new Date();
        now.setHours(now.getHours() + 1);

        const pad = n => n < 10 ? '0' + n : n;
        const yyyy = now.getFullYear();
        const mm = pad(now.getMonth() + 1);
        const dd = pad(now.getDate());
        const hh = pad(now.getHours());
        const min = pad(now.getMinutes());

        const dateInput = document.getElementById('reminderDate');
        const timeInput = document.getElementById('reminderTime');
        const noteInput = document.getElementById('reminderNote');

        if (dateInput) dateInput.value = `${yyyy}-${mm}-${dd}`;
        if (timeInput) timeInput.value = `${hh}:${min}`;
        if (noteInput) noteInput.value = '';

        this.updateReminderPreview();
        modal.classList.add('open');
    },

    closeReminderModal() {
        const modal = document.getElementById('setReminderModal');
        if (modal) modal.classList.remove('open');
        this.activeReminderThreadId = null;
    },

    updateReminderPreview() {
        const dVal = document.getElementById('reminderDate')?.value;
        const tVal = document.getElementById('reminderTime')?.value;
        const previewEl = document.getElementById('reminderFormattedPreview');
        if (!previewEl) return;

        if (!dVal || !tVal) {
            previewEl.innerText = 'Please select date & time';
            return;
        }

        const [y, m, d] = dVal.split('-');
        const [hourStr, minStr] = tVal.split(':');
        let hours = parseInt(hourStr, 10);
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const formattedTime = `${hours < 10 ? '0' + hours : hours}:${minStr} ${ampm}`;

        previewEl.innerHTML = `<strong>Date:</strong> ${d}/${m}/${y} &nbsp;&bull;&nbsp; <strong>Time:</strong> ${formattedTime}`;
    },

    async handleSetReminder(e) {
        e.preventDefault();
        const user = this.getUser();
        if (!user || !this.activeReminderThreadId) return;

        const dVal = document.getElementById('reminderDate')?.value;
        const tVal = document.getElementById('reminderTime')?.value;
        const note = document.getElementById('reminderNote')?.value.trim();

        if (!dVal || !tVal) {
            return alert('Please select a specific date and time for the reminder.');
        }

        const remind_at = `${dVal} ${tVal}:00`;

        // Format for confirmation alert: e.g. 25/08/2026, 10:30 PM
        const [y, m, d] = dVal.split('-');
        const [h, min] = tVal.split(':');
        let hourNum = parseInt(h, 10);
        const ampm = hourNum >= 12 ? 'PM' : 'AM';
        hourNum = hourNum % 12 || 12;
        const readableTime = `${hourNum < 10 ? '0' + hourNum : hourNum}:${min} ${ampm}`;

        try {
            const res = await fetch('/api/forums/reminder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    thread_id: this.activeReminderThreadId,
                    remind_at: remind_at,
                    note: note || 'Discussion thread reminder'
                })
            });
            const data = await res.json();
            alert(`Reminder successfully scheduled for ${d}/${m}/${y} at ${readableTime}!`);
            this.closeReminderModal();
        } catch (err) {
            console.error('Set reminder error', err);
        }
    },

    startReminderPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);

        // Real-time reminder delivery check every 5 seconds
        this.pollingInterval = setInterval(async () => {
            const user = this.getUser();
            if (!user) return;

            try {
                const res = await fetch(`/api/forums/reminders?user_id=${user.user_id}`);
                const data = await res.json();
                if (data.success && data.reminders && data.reminders.length > 0) {
                    data.reminders.forEach(r => {
                        const dateStr = r.remind_at || '';
                        alert(`FORUM THREAD REMINDER\n\nThread: ${r.thread_title}\nSpace: ${r.category || 'General'}\nScheduled Time: ${dateStr}\nNote: ${r.note || 'No notes'}`);
                    });
                }
            } catch (err) {
                // Silently ignore network poll errors
            }
        }, 5000);
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
