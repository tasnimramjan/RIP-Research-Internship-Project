// Discussion Forums Logic & Socket.io Reminders
const Forums = {
    currentUser: null,
    currentCategory: 'All',
    allowedCategories: [],

    async init(user) {
        this.currentUser = user;
        if (!this.currentUser) return;

        await this.fetchAllowedCategories();
        this.renderLayout();
        this.setupEventListeners();
        this.loadThreads();
        this.setupSocketIO();
    },

    async fetchAllowedCategories() {
        try {
            const res = await fetch(`/api/forums/access?user_id=${this.currentUser.user_id}`);
            const data = await res.json();
            if (data.success) {
                this.allowedCategories = data.categories || [];
            }
        } catch (err) {
            console.error("Failed to fetch allowed categories", err);
        }
    },

    renderLayout() {
        const appContainer = document.getElementById('forums-app');
        if (!appContainer) return;
        
        // Build the Sidebar based on allowed categories
        let sidebarHtml = `
            <div class="forum-sidebar" style="min-width:250px; background:var(--bg-card); padding:1rem; border-radius:8px; border:1px solid var(--border-color);">
                <h3 style="font-size:1rem; font-weight:700; margin-bottom:1rem;">Categories</h3>
                <ul style="list-style:none; padding:0; display:flex; flex-direction:column; gap:0.5rem;" id="forumSidebarList">
                    <li class="active" data-category="All" style="padding:0.5rem; border-radius:4px; cursor:pointer;">All Topics</li>
        `;
        
        this.allowedCategories.forEach(cat => {
            if (cat !== 'General Academic Discussions') {
                sidebarHtml += `<li data-category="${cat}" style="padding:0.5rem; border-radius:4px; cursor:pointer;">${cat}</li>`;
            }
        });
        
        // Always add General Academic Discussions at the end
        if (this.allowedCategories.includes('General Academic Discussions')) {
             sidebarHtml += `<li data-category="General Academic Discussions" style="padding:0.5rem; border-radius:4px; cursor:pointer;">General Academic Discussions</li>`;
        }
        
        sidebarHtml += `
                </ul>
            </div>
        `;
        
        // Main content area
        const mainHtml = `
            <div class="forum-main" style="flex:1;">
                <div id="threadsContainer" style="display:flex; flex-direction:column; gap:1rem;"></div>
            </div>
        `;
        
        appContainer.innerHTML = `
            <div style="display:flex; gap:1.5rem; align-items:flex-start;">
                ${sidebarHtml}
                ${mainHtml}
            </div>
        `;

        // Style the active state manually since we are not using an external css for these list items
        document.querySelectorAll('#forumSidebarList li').forEach(li => {
            li.onmouseenter = () => { if(!li.classList.contains('active')) li.style.background = 'rgba(255,255,255,0.05)'; };
            li.onmouseleave = () => { if(!li.classList.contains('active')) li.style.background = 'transparent'; };
            if(li.classList.contains('active')) li.style.background = 'var(--accent-cyan)';
        });

        // Update Create Thread dropdown
        const categorySelect = document.getElementById('threadCategory');
        if (categorySelect) {
            categorySelect.innerHTML = '';
            if (this.currentUser.role === 'Admin') {
                categorySelect.innerHTML += `<option value="General Academic Discussions">General Academic Discussions</option>`;
            } else {
                this.allowedCategories.forEach(cat => {
                    categorySelect.innerHTML += `<option value="${cat}">${cat}</option>`;
                });
            }
        }
    },

    setupEventListeners() {
        // Sidebar Category Clicks
        document.querySelectorAll('#forumSidebarList li').forEach(li => {
            li.addEventListener('click', (e) => {
                document.querySelectorAll('#forumSidebarList li').forEach(el => {
                    el.classList.remove('active');
                    el.style.background = 'transparent';
                });
                e.target.classList.add('active');
                e.target.style.background = 'var(--accent-cyan)';
                this.currentCategory = e.target.dataset.category;
                this.loadThreads();
            });
        });

        // Create Thread Modal
        const modal = document.getElementById('createThreadModal');
        const openBtn = document.getElementById('openCreateThreadBtn');
        const closeBtn = document.getElementById('closeThreadModalBtn');

        if (openBtn) {
            openBtn.onclick = () => modal.classList.add('open');
        }
        if (closeBtn) {
            closeBtn.onclick = () => modal.classList.remove('open');
        }

        // Form Submit
        const form = document.getElementById('createThreadForm');
        if(form) {
            form.onsubmit = async (e) => {
                e.preventDefault();
                await this.createThread(
                    document.getElementById('threadTitle').value,
                    document.getElementById('threadCategory').value,
                    document.getElementById('threadContent').value
                );
                modal.classList.remove('open');
                form.reset();
            };
        }
    },

    setupSocketIO() {
        if (!window.sio_client) {
            window.sio_client = io('http://127.0.0.1:8002');
            window.sio_client.on('connect', () => {
                window.sio_client.emit('join_chat', { user_id: this.currentUser.user_id });
            });
        }
        
        window.sio_client.off('forum_reminder');
        window.sio_client.on('forum_reminder', (payload) => {
            alert(`⏰ FORUM REMINDER ⏰\n\nThread: ${payload.thread_title}\nNote: ${payload.note}`);
        });
    },

    async loadThreads() {
        try {
            const url = this.currentCategory === 'All' 
                ? `/api/forums/threads?user_id=${this.currentUser.user_id}` 
                : `/api/forums/threads?user_id=${this.currentUser.user_id}&category=${encodeURIComponent(this.currentCategory)}`;
            
            const res = await fetch(url, { cache: 'no-store' });
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
            container.innerHTML = '<p style="color: var(--text-muted); padding: 2rem; background: var(--bg-card); border-radius: 8px;">No discussion threads found in this category.</p>';
            return;
        }

        const isAdmin = this.currentUser.role === 'Admin';
        
        threads.forEach(thread => {
            const likeCount = thread.reactions && thread.reactions.like ? thread.reactions.like : 0;
            const commentsCount = thread.comments ? thread.comments.length : 0;
            
            let deleteThreadHtml = isAdmin ? `<button class="btn btn-sm btn-danger" onclick="Forums.deleteThread('${thread.thread_id}')">Delete Thread</button>` : '';
            
            let canComment = true;
            if (isAdmin && thread.category !== 'General Academic Discussions') {
                canComment = false;
            }
            
            let commentInputHtml = canComment ? `
                <div class="comment-input-group" style="display:flex; gap:0.5rem; margin-top:1rem;">
                    <input type="text" id="comment-input-${thread.thread_id}" placeholder="Write a comment..." style="flex:1; padding:0.5rem; border-radius:4px; border:1px solid var(--border-color); background:transparent; color:white;">
                    <button class="btn btn-sm btn-cyan" onclick="Forums.postComment('${thread.thread_id}')">Post</button>
                </div>
            ` : '<p style="color:var(--text-muted); font-size:0.8rem; font-style:italic; margin-top:1rem;">Admins cannot comment on this category.</p>';

            const card = document.createElement('div');
            card.className = 'thread-card';
            card.style = 'background:var(--bg-card); border:1px solid var(--border-color); border-radius:8px; padding:1.2rem;';
            card.innerHTML = `
                <div class="thread-meta">
                    <span class="badge" style="background:var(--accent-purple); padding:0.2rem 0.5rem; border-radius:4px; font-size:0.75rem; font-weight:700;">${thread.category}</span>
                    <span style="color:var(--text-muted); font-size:0.8rem; margin-left:0.5rem;">Posted by <strong style="color:var(--text-light);">${thread.author_name}</strong> (${thread.author_role}) • ${new Date(thread.created_at).toLocaleString()}</span>
                </div>
                <h3 class="thread-title" style="margin-top:0.8rem; margin-bottom:0.5rem; font-size:1.1rem; color:var(--text-light);">${thread.title}</h3>
                <div class="thread-content" style="margin-bottom:1rem; font-size:0.9rem; line-height:1.5;">${thread.content}</div>
                
                <div class="thread-actions" style="display:flex; gap:1rem; border-top:1px solid var(--border-color); padding-top:0.8rem; align-items:center;">
                    <button class="btn btn-sm btn-secondary" onclick="Forums.reactToThread('${thread.thread_id}')">
                        ❤️ <span>${likeCount}</span>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="Forums.toggleComments('${thread.thread_id}')">
                        💬 <span>${commentsCount} Comments</span>
                    </button>
                    ${!isAdmin ? `<button class="btn btn-sm btn-cyan" onclick="Forums.promptReminder('${thread.thread_id}')" style="margin-left:auto;">
                        ⏰ Remind Me
                    </button>` : ''}
                    ${deleteThreadHtml}
                </div>

                <div class="comments-section" id="comments-${thread.thread_id}" style="display:none; margin-top:1rem; padding:1rem; background:rgba(0,0,0,0.2); border-radius:8px;">
                    <div class="comments-list" style="margin-bottom:1rem;">
                        ${this.renderComments(thread.comments, isAdmin)}
                    </div>
                    ${commentInputHtml}
                </div>
            `;
            container.appendChild(card);
        });
    },

    renderComments(comments, isAdmin) {
        if (!comments || comments.length === 0) return '<p style="color: var(--text-muted); font-size: 0.85rem;">No comments yet.</p>';
        return comments.map(c => {
            let deleteBtn = isAdmin ? `<button class="btn btn-sm btn-danger" style="margin-left:auto; padding:0.1rem 0.4rem; font-size:0.7rem;" onclick="Forums.deleteComment('${c.comment_id}')">Delete</button>` : '';
            return `
                <div class="comment" style="padding:0.5rem 0; border-bottom:1px solid var(--border-color); display:flex; flex-direction:column;">
                    <div class="comment-meta" style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.3rem; display:flex; align-items:center;">
                        <strong style="color:var(--text-light); margin-right:0.3rem;">${c.author_name}</strong> • ${new Date(c.created_at).toLocaleString()}
                        ${deleteBtn}
                    </div>
                    <div class="comment-content" style="font-size:0.9rem;">${c.content}</div>
                </div>
            `;
        }).join('');
    },

    toggleComments(threadId) {
        const section = document.getElementById(`comments-${threadId}`);
        if(section) {
            section.style.display = section.style.display === 'none' ? 'block' : 'none';
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
                await this.loadThreads(); 
                this.toggleComments(threadId); // Re-open
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
                this.loadThreads(); 
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
        
        document.getElementById('setReminderModal').classList.add('open');
    },

    async submitReminder() {
        const datetimeInput = document.getElementById('reminderDatetime').value;
        const note = document.getElementById('reminderNote').value;
        if(!datetimeInput) return alert('Please select a valid date and time.');

        const dateObj = new Date(datetimeInput);
        const pad = n => n<10 ? '0'+n : n;
        const remind_at = `${dateObj.getFullYear()}-${pad(dateObj.getMonth()+1)}-${pad(dateObj.getDate())} ${pad(dateObj.getHours())}:${pad(dateObj.getMinutes())}:${pad(dateObj.getSeconds())}`;

        await this.setReminder(this.activeReminderThread, remind_at, note);
        document.getElementById('setReminderModal').classList.remove('open');
    },

    async setReminder(threadId, remind_at, note) {
        try {
            const res = await fetch('/api/forums/reminder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, thread_id: threadId, remind_at, note: note || "User requested reminder" })
            });
            const data = await res.json();
            alert(data.message);
        } catch(err) {
            console.error(err);
        }
    },

    async deleteThread(threadId) {
        if(!confirm("Are you sure you want to delete this thread?")) return;
        try {
            const res = await fetch('/api/forums/delete_thread', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, thread_id: threadId })
            });
            const data = await res.json();
            if(data.success) {
                this.loadThreads();
            } else {
                alert(data.message);
            }
        } catch(err) {
            console.error(err);
        }
    },

    async deleteComment(commentId) {
        if(!confirm("Are you sure you want to delete this comment?")) return;
        try {
            const res = await fetch('/api/forums/delete_comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.currentUser.user_id, comment_id: commentId })
            });
            const data = await res.json();
            if(data.success) {
                this.loadThreads();
            } else {
                alert(data.message);
            }
        } catch(err) {
            console.error(err);
        }
    }
};

window.Forums = Forums;
