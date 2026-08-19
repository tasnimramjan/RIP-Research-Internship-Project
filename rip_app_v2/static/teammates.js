window.Teammates = {
    currentUser: null,
    pollingInterval: null,
    activeChatUserId: null,
    activeChatUserName: null,

    init(user) {
        this.currentUser = user;
        // Bind UI events for Teammate Finder
        document.getElementById('openPostProjectBtn')?.addEventListener('click', () => {
            document.getElementById('postProjectModal').classList.add('active');
        });
        document.getElementById('closePostProjectBtn')?.addEventListener('click', () => {
            document.getElementById('postProjectModal').classList.remove('active');
        });
        document.getElementById('postProjectForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitProject();
        });
        
        // Chat UI bindings
        document.getElementById('closeChatBtn')?.addEventListener('click', () => {
            this.closeChat();
        });
        document.getElementById('chatSendBtn')?.addEventListener('click', () => {
            this.sendMessage();
        });
        document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') this.sendMessage();
        });
    },

    async loadProjects() {
        if(!this.currentUser) return;
        try {
            const res = await fetch('/api/projects/all');
            const data = await res.json();
            const container = document.getElementById('projectBoardContainer');
            if(!container) return;
            
            if(data.success && data.posts.length > 0) {
                container.innerHTML = data.posts.map(p => `
                    <div class="project-card">
                        <div class="project-title">${p.idea_title}</div>
                        <div class="project-meta">Posted by ${p.author_name} | ${p.created_at}</div>
                        <div class="project-desc">${p.description}</div>
                        <div class="skills-req">
                            ${(Array.isArray(p.required_skills) ? p.required_skills : []).map(s => `<span class="tag">${s.trim()}</span>`).join('')}
                        </div>
                        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                            ${p.student_id !== this.currentUser.user_id ? 
                                `<button class="btn btn-sm btn-cyan" onclick="Teammates.openChat('${p.student_id}', '${p.author_name}')">Message Creator</button>
                                 <button class="btn btn-sm btn-secondary" onclick="Teammates.joinProject('${p.post_id}')">Request to Join</button>`
                            : `<span style="font-size:0.8rem; color:var(--accent-indigo); font-weight:600; padding: 0.4rem 0;">Your Project</span>`}
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = `<p style="color:var(--text-muted); padding: 2rem;">No project ideas posted yet. Be the first!</p>`;
            }
        } catch(err) {
            console.error(err);
        }
    },

    async submitProject() {
        const title = document.getElementById('projTitle').value;
        const desc = document.getElementById('projDesc').value;
        const skills = document.getElementById('projSkills').value;
        
        try {
            const res = await fetch('/api/projects/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ student_id: this.currentUser.user_id, idea_title: title, description: desc, required_skills: skills })
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('postProjectModal').classList.remove('active');
                document.getElementById('postProjectForm').reset();
                this.loadProjects();
            } else {
                alert(data.message);
            }
        } catch(err) {
            console.error(err);
        }
    },

    async joinProject(postId) {
        try {
            const res = await fetch('/api/projects/join', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ student_id: this.currentUser.user_id, post_id: postId })
            });
            const data = await res.json();
            alert(data.message);
        } catch(err) {
            console.error(err);
        }
    },

    // 1-to-1 Messaging Logic
    openChat(userId, userName) {
        this.activeChatUserId = userId;
        this.activeChatUserName = userName;
        document.getElementById('chatUserName').innerText = userName;
        document.getElementById('chatWindow').classList.add('open');
        this.fetchMessages();
        
        // Polling interval strictly for the active chat
        if(this.pollingInterval) clearInterval(this.pollingInterval);
        this.pollingInterval = setInterval(() => this.fetchMessages(), 3000);
    },

    closeChat() {
        document.getElementById('chatWindow').classList.remove('open');
        this.activeChatUserId = null;
        if(this.pollingInterval) clearInterval(this.pollingInterval);
    },

    async fetchMessages() {
        if(!this.activeChatUserId) return;
        try {
            const res = await fetch(`/api/messages/history?user1=${this.currentUser.user_id}&user2=${this.activeChatUserId}`);
            const data = await res.json();
            if(data.success) {
                this.renderMessages(data.messages);
            }
        } catch(err) {
            console.error(err);
        }
    },

    renderMessages(messages) {
        const container = document.getElementById('chatMessages');
        if(!messages || messages.length === 0) {
            container.innerHTML = `<p style="text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:2rem;">No messages yet. Say hi!</p>`;
            return;
        }
        
        // Save current scroll position to see if we were at the bottom
        const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10;

        container.innerHTML = messages.map(m => {
            const isSent = m.sender_id === this.currentUser.user_id;
            return `
                <div class="msg-bubble ${isSent ? 'sent' : 'received'}">
                    <div>${m.message_text}</div>
                    <div class="msg-time">${m.timestamp.slice(11,16)}</div>
                </div>
            `;
        }).join('');
        
        // Auto-scroll to bottom if they were at the bottom
        if (isAtBottom) {
            container.scrollTop = container.scrollHeight;
        }
    },

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const text = input.value.trim();
        if(!text || !this.activeChatUserId) return;
        
        input.value = ''; // clear immediately
        
        try {
            const res = await fetch('/api/messages/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ sender_id: this.currentUser.user_id, receiver_id: this.activeChatUserId, message_text: text })
            });
            const data = await res.json();
            if(data.success) {
                this.fetchMessages(); // refresh instantly on send
            }
        } catch(err) {
            console.error(err);
        }
    }
};
