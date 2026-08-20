// Discussion Forums Logic & Polling Reminders
const Forums = {
    currentUser: null,
    currentCategory: 'All',
    pollingInterval: null,

    init(user) {
        this.currentUser = user;
        if (!this.currentUser) return;

        this.setupEventListeners();
        this.loadThreads();
        this.startReminderPolling();
    },

    setupEventListeners() {
        // Sidebar Category Clicks
        document.querySelectorAll('.forum-sidebar li').forEach(li => {
            li.addEventListener('click', (e) => {
                document.querySelectorAll('.forum-sidebar li').forEach(el => el.classList.remove('active'));
                e.target.classList.add('active');
                this.currentCategory = e.target.dataset.category;
                this.loadThreads();
            });
        });

        // Create Thread Modal
        const modal = document.getElementById('createThreadModal');
        const openBtn = document.getElementById('openCreateThreadBtn');
        const closeBtn = document.getElementById('closeThreadModalBtn');

        if(openBtn) openBtn.addEventListener('click', () => modal.classList.add('active'));
        if(closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('active'));

        // Form Submit
        const form = document.getElementById('createThreadForm');
        if(form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.createThread(
                    document.getElementById('threadTitle').value,
                    document.getElementById('threadCategory').value,
                    document.getElementById('threadContent').value
                );
                modal.classList.remove('active');
                form.reset();
            });
        }
    },

    async loadThreads() {
        try {
            const url = this.currentCategory === 'All' 
                ? '/api/forums/threads' 
                : `/api/forums/threads?category=${encodeURIComponent(this.currentCategory)}`;
            
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.success) {
                this.renderThreads(data.threads);
            }
        } catch (err) {
            console.error("Failed to load threads", err);
        }
    },

    renderThreads(threads) {
        const container = document.getElementById('threadsContainer');
        if (!container) return;
        container.innerHTML = '';

        if(threads.length === 0) {
            container.innerHTML = '<p style="color: #6b7280;">No discussion threads found in this category.</p>';
            return;
        }

        threads.forEach(thread => {
            const likeCount = thread.reactions && thread.reactions.like ? thread.reactions.like : 0;
            const commentsCount = thread.comments ? thread.comments.length : 0;

            const card = document.createElement('div');
            card.className = 'thread-card';
            card.innerHTML = `
                <div class="thread-meta">
                    <span class="badge">${thread.category}</span>
                    <span>Posted by <strong>${thread.author_name}</strong> (${thread.author_role})</span>
                    <span>${new Date(thread.created_at).toLocaleString()}</span>
                </div>
                <h3 class="thread-title">${thread.title}</h3>
                <div class="thread-content">${thread.content}</div>
                <div class="thread-actions">
                    <button class="action-btn react-btn" onclick="Forums.reactToThread('${thread.thread_id}')">
                        ❤️ <span>${likeCount}</span>
                    </button>
                    <button class="action-btn" onclick="Forums.toggleComments('${thread.thread_id}')">
                        💬 <span>${commentsCount} Comments</span>
                    </button>
                    <button class="action-btn remind-btn" onclick="Forums.promptReminder('${thread.thread_id}')">
                        ⏰ Remind Me
                    </button>
                    ${(window.currentUser && (window.currentUser.user_id === thread.user_id || window.currentUser.role === 'Admin')) ? `
                        <button class="btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick="Forums.deleteThread('${thread.thread_id}')">
                            Delete
                        </button>
                    ` : ''}
                </div>
                <div class="comments-section" id="comments-${thread.thread_id}">
                    <div class="comments-list">
                        ${this.renderComments(thread.comments)}
                    </div>
                    <div class="comment-input-group">
                        <input type="text" id="comment-input-${thread.thread_id}" placeholder="Write a comment...">
                        <button class="btn-primary" onclick="Forums.postComment('${thread.thread_id}')">Post</button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    },

    async deleteThread(threadId) {
        if (!confirm('Are you sure you want to delete this discussion thread?')) return;
        try {
            const res = await fetch('/api/forums/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: window.currentUser.user_id, thread_id: threadId })
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                this.loadThreads(document.querySelector('.tab-btn.active')?.dataset.category || 'All');
            }
        } catch (err) {
            console.error('Delete error', err);
        }
    },

    renderComments(comments) {
        if (!comments || comments.length === 0) return '<p style="color: #9ca3af; font-size: 0.9rem;">No comments yet.</p>';
        return comments.map(c => `
            <div class="comment">
                <div class="comment-meta"><strong>${c.author_name}</strong> • ${new Date(c.created_at).toLocaleString()}</div>
                <div class="comment-content">${c.content}</div>
            </div>
        `).join('');
    },

    toggleComments(threadId) {
        const section = document.getElementById(`comments-${threadId}`);
        if(section) {
            section.classList.toggle('open');
        }
    },

    async createThread(title, category, content) {
        try {
            const res = await fetch('/api/forums/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, title, category, content })
            });
            const data = await res.json();
            if(data.success) {
                this.loadThreads();
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error(err);
        }
    },

    async postComment(threadId) {
        const input = document.getElementById(`comment-input-${threadId}`);
        const content = input.value.trim();
        if(!content) return;

        try {
            const res = await fetch('/api/forums/comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, thread_id: threadId, content })
            });
            const data = await res.json();
            if(data.success) {
                this.loadThreads(); // Reload to show comment
            }
        } catch (err) {
            console.error(err);
        }
    },

    async reactToThread(threadId) {
        try {
            const res = await fetch('/api/forums/react', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, thread_id: threadId, reaction_type: 'like' })
            });
            const data = await res.json();
            if(data.success) {
                this.loadThreads(); // Reload silently to show updated reactions
            }
        } catch (err) {
            console.error(err);
        }
    },

    promptReminder(threadId) {
        this.activeReminderThread = threadId;
        
        const now = new Date();
        now.setHours(now.getHours() + 1);
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        document.getElementById('reminderDatetime').value = now.toISOString().slice(0, 16);
        document.getElementById('reminderNote').value = "";
        
        document.getElementById('setReminderModal').classList.add('active');
    },

    async submitReminder() {
        const datetimeInput = document.getElementById('reminderDatetime').value;
        const note = document.getElementById('reminderNote').value;
        if(!datetimeInput) return alert('Please select a valid date and time.');

        const dateObj = new Date(datetimeInput);
        const pad = n => n<10 ? '0'+n : n;
        const remind_at = `${dateObj.getFullYear()}-${pad(dateObj.getMonth()+1)}-${pad(dateObj.getDate())} ${pad(dateObj.getHours())}:${pad(dateObj.getMinutes())}:${pad(dateObj.getSeconds())}`;

        await this.setReminder(this.activeReminderThread, remind_at, note);
        document.getElementById('setReminderModal').classList.remove('active');
    },

    async setReminder(threadId, remind_at, note) {
        try {
            const res = await fetch('/api/forums/remind', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, thread_id: threadId, remind_at, note: note || "User requested reminder" })
            });
            const data = await res.json();
            console.log(data.message); // No popup
        } catch(err) {
            console.error(err);
        }
    },

    startReminderPolling() {
        if(this.pollingInterval) clearInterval(this.pollingInterval);
        
        // Poll every 10 seconds
        this.pollingInterval = setInterval(async () => {
            if(!this.currentUser) return;
            try {
                const res = await fetch(`/api/forums/reminders?user_id=${this.currentUser.user_id}`);
                const data = await res.json();
                if(data.success && data.reminders && data.reminders.length > 0) {
                    data.reminders.forEach(r => {
                        // Native browser alert as a reminder
                        alert(`⏰ FORUM REMINDER ⏰\n\nThread: ${r.thread_title}\nNote: ${r.note}`);
                    });
                }
            } catch(err) {
                // Silently fail if network issue
            }
        }, 10000);
    }
};

window.Forums = Forums;
