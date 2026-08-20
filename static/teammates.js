window.Teammates = {
    currentUser: null,
    activeChatUserId: null,
    activeChatUserName: null,
    socket: null,

    init(user) {
        this.currentUser = user;
        
        // Hide features if user is faculty
        if(this.currentUser && this.currentUser.role === 'Faculty') {
            document.getElementById('openPostProjectBtn').style.display = 'none';
        }

        // Initialize Socket.io connecting to port 8002
        this.socket = io('http://127.0.0.1:8002');
        this.socket.on('connect', () => {
            console.log('Socket.io connected');
            this.socket.emit('join_chat', { user_id: this.currentUser.user_id });
        });

        this.socket.on('new_message', (msg) => {
            if (this.activeChatUserId === msg.sender_id || this.activeChatUserId === msg.receiver_id) {
                this.appendMessageToChat(msg);
            }
        });

        // Bind UI events for Teammate Finder
        document.getElementById('openPostProjectBtn')?.addEventListener('click', () => {
            document.getElementById('postProjectModal').classList.add('open');
        });
        document.getElementById('closePostProjectBtn')?.addEventListener('click', () => {
            document.getElementById('postProjectModal').classList.remove('open');
        });
        document.getElementById('postProjectForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitProject();
        });
        
        // Chat UI bindings
        document.getElementById('closeDirectChatBtn')?.addEventListener('click', () => {
            this.closeChat();
        });
        document.getElementById('directChatSendBtn')?.addEventListener('click', () => {
            this.sendMessage();
        });
        document.getElementById('directChatInput')?.addEventListener('keypress', (e) => {
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
                let html = '';
                data.posts.forEach(p => {
                    const isOwner = p.student_id === this.currentUser.user_id;
                    const myRequest = p.teammates.find(t => t.student_id === this.currentUser.user_id);
                    
                    let actionHtml = '';
                    if (this.currentUser.role === 'Faculty') {
                        actionHtml = `<span style="font-size:0.8rem; color:var(--text-muted);">Faculty cannot join student projects.</span>`;
                    } else if (isOwner) {
                        actionHtml = `<div style="width:100%;">
                            <h4 style="font-size:0.85rem; font-weight:600; margin-bottom:0.5rem; color:var(--accent-indigo);">Manage Requests & Team</h4>
                            ${p.teammates.length === 0 ? `<p style="font-size:0.8rem; color:var(--text-muted);">No members or requests yet.</p>` : ''}
                            ${p.teammates.map(t => {
                                if (t.status === 'Pending') {
                                    return `<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; padding:0.4rem; background:var(--bg-card); border-radius:4px; margin-bottom:0.3rem;">
                                        <span>${t.name} (Pending)</span>
                                        <div style="display:flex; gap:0.3rem;">
                                            <button class="btn btn-sm btn-cyan" onclick="Teammates.respondToRequest('${p.post_id}', '${t.student_id}', 'accept')">Accept</button>
                                            <button class="btn btn-sm btn-secondary" onclick="Teammates.respondToRequest('${p.post_id}', '${t.student_id}', 'reject')">Reject</button>
                                        </div>
                                    </div>`;
                                } else if (t.status === 'Accepted') {
                                    return `<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; padding:0.4rem; background:var(--bg-card); border-radius:4px; margin-bottom:0.3rem;">
                                        <span>${t.name} (Teammate)</span>
                                        <button class="btn btn-sm btn-cyan" onclick="Teammates.openChat('${t.student_id}', '${t.name}')">Chat</button>
                                    </div>`;
                                }
                                return '';
                            }).join('')}
                        </div>`;
                    } else {
                        if (!myRequest) {
                            actionHtml = `<button class="btn btn-sm btn-cyan" onclick="Teammates.joinProject('${p.post_id}')">Request to Join</button>`;
                        } else if (myRequest.status === 'Pending') {
                            actionHtml = `<span style="font-size:0.85rem; font-weight:600; color:#eab308; padding: 0.4rem 0;">Request Sent (Pending)</span>`;
                        } else if (myRequest.status === 'Accepted') {
                            actionHtml = `<button class="btn btn-sm btn-cyan" onclick="Teammates.openChat('${p.student_id}', '${p.author_name}')">Chat with Creator</button>
                            <span style="font-size:0.85rem; font-weight:600; color:var(--accent-cyan); padding: 0.4rem 0.4rem;">You are a Teammate!</span>`;
                        } else if (myRequest.status === 'Rejected') {
                            actionHtml = `<span style="font-size:0.85rem; font-weight:600; color:red; padding: 0.4rem 0;">Request Rejected</span>`;
                        }
                    }

                    html += `
                        <div class="project-card">
                            <div class="project-title">${p.idea_title}</div>
                            <div class="project-meta">Posted by ${p.author_name} | ${p.created_at}</div>
                            <div class="project-desc">${p.description}</div>
                            <div class="skills-req">
                                ${(Array.isArray(p.required_skills) ? p.required_skills : []).map(s => `<span class="tag">${s.trim()}</span>`).join('')}
                            </div>
                            <div style="display: flex; flex-direction:column; gap: 0.5rem; margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top:0.8rem;">
                                ${actionHtml}
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
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
                document.getElementById('postProjectModal').classList.remove('open');
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
            if (data.success) this.loadProjects();
        } catch(err) {
            console.error(err);
        }
    },

    async respondToRequest(postId, studentId, action) {
        try {
            const res = await fetch('/api/projects/respond', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ post_id: postId, student_id: studentId, action: action })
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) this.loadProjects();
        } catch(err) {
            console.error(err);
        }
    },

    // 1-to-1 Messaging Logic
    openChat(userId, userName) {
        this.activeChatUserId = userId;
        this.activeChatUserName = userName;
        document.getElementById('directChatUserName').innerText = userName;
        document.getElementById('directChatWindow').classList.add('open');
        this.fetchMessages();
    },

    closeChat() {
        document.getElementById('directChatWindow').classList.remove('open');
        this.activeChatUserId = null;
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
        const container = document.getElementById('directChatMessages');
        if(!messages || messages.length === 0) {
            container.innerHTML = `<p style="text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:2rem;">No messages yet. Say hi!</p>`;
            return;
        }

        container.innerHTML = '';
        messages.forEach(m => this.appendMessageToChat(m, false));
        container.scrollTop = container.scrollHeight;
    },

    appendMessageToChat(msg, autoScroll = true) {
        const container = document.getElementById('directChatMessages');
        if (container.innerHTML.includes('No messages yet')) {
            container.innerHTML = '';
        }

        const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10;
        const isSent = msg.sender_id === this.currentUser.user_id;
        
        let timestamp = msg.timestamp;
        if (timestamp && timestamp.length > 16) {
            timestamp = timestamp.slice(11, 16);
        }

        const msgHtml = `
            <div class="msg-bubble ${isSent ? 'sent' : 'received'}">
                <div>${msg.message_text}</div>
                <div class="msg-time">${timestamp || ''}</div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', msgHtml);

        if (autoScroll && isAtBottom) {
            container.scrollTop = container.scrollHeight;
        } else if (!autoScroll) {
            // just append
        } else {
            container.scrollTop = container.scrollHeight; // force scroll on send
        }
    },

    sendMessage() {
        const input = document.getElementById('directChatInput');
        const text = input.value.trim();
        if(!text || !this.activeChatUserId) return;
        
        input.value = ''; // clear immediately
        
        const now = new Date();
        const timestamp = now.toISOString().replace('T', ' ').slice(0, 19);

        // Emit via socket.io instead of REST POST to save and broadcast
        this.socket.emit('send_message', {
            sender_id: this.currentUser.user_id,
            receiver_id: this.activeChatUserId,
            message_text: text,
            timestamp: timestamp
        });
    }
};
