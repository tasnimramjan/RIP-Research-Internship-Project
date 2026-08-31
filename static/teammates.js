// ==========================================================
// Project Teammate Finder & Join Requests Logic
// - Student: Can Post Idea, Message Creator (before & after joining), Request to Join, Accept/Reject Join Requests
// - Creator: Single clean "Messages" option to see messages and inquiries
// - Dedicated "Join Requests" Notification Menu in Top Navigation Bar (No emojis)
// - Admin: Can View All Posts, Delete Posts
// - Faculty: View Only
// ==========================================================

window.Teammates = {
    currentUser: null,
    joinRequestsPollingInterval: null,

    getUser() {
        this.currentUser = window.currentUser || (typeof currentUser !== 'undefined' ? currentUser : null) || JSON.parse(localStorage.getItem('rip_user') || 'null');
        return this.currentUser;
    },

    init(user) {
        if (user) this.currentUser = user;
        else this.getUser();
        
        const userRole = this.currentUser ? this.currentUser.role : null;
        
        // Post Project Modal Buttons
        const openBtn = document.getElementById('openPostProjectBtn');
        if (openBtn) {
            openBtn.style.display = (userRole === 'Student') ? 'inline-block' : 'none';
            openBtn.onclick = () => {
                const u = this.getUser();
                if (!u || u.role !== 'Student') {
                    return alert('Only students can post project ideas in Teammate Finder.');
                }
                document.getElementById('postProjectModal')?.classList.add('open');
            };
        }
        
        const closeBtn = document.getElementById('closePostProjectBtn');
        if (closeBtn) {
            closeBtn.onclick = () => {
                document.getElementById('postProjectModal')?.classList.remove('open');
            };
        }

        const form = document.getElementById('postProjectForm');
        if (form) {
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitProject();
            };
        }

        // Start Join Requests Notification Polling if user is Student
        if (userRole === 'Student') {
            this.startJoinRequestsPolling();
        } else {
            this.stopJoinRequestsPolling();
        }
    },

    // ── Dedicated Join Requests Top-Bar Menu Logic ──
    toggleJoinRequestsMenu() {
        const dropdown = document.getElementById('joinRequestsDropdown');
        if (!dropdown) return;
        dropdown.classList.toggle('open');
        if (dropdown.classList.contains('open')) {
            this.fetchJoinRequests();
        }
    },

    closeJoinRequestsMenu() {
        document.getElementById('joinRequestsDropdown')?.classList.remove('open');
    },

    startJoinRequestsPolling() {
        this.stopJoinRequestsPolling();
        this.fetchJoinRequests();
        // Poll every 5 seconds for new join requests
        this.joinRequestsPollingInterval = setInterval(() => {
            this.fetchJoinRequests();
        }, 5000);
    },

    stopJoinRequestsPolling() {
        if (this.joinRequestsPollingInterval) {
            clearInterval(this.joinRequestsPollingInterval);
            this.joinRequestsPollingInterval = null;
        }
        const navCont = document.getElementById('joinRequestsNavContainer');
        if (navCont) navCont.style.display = 'none';
    },

    async fetchJoinRequests() {
        const user = this.getUser();
        if (!user || user.role !== 'Student') {
            this.stopJoinRequestsPolling();
            return;
        }

        // Show Join Requests button in nav bar
        const navCont = document.getElementById('joinRequestsNavContainer');
        if (navCont) navCont.style.display = 'block';

        try {
            const res = await fetch(`/api/projects/requests?user_id=${user.user_id}`);
            const data = await res.json();
            if (!data.success) return;

            const incoming = data.incoming || [];
            const outgoing = data.outgoing || [];
            const pendingCount = data.pending_count || 0;

            // Update badge counter
            const badge = document.getElementById('joinRequestsBadge');
            if (badge) {
                if (pendingCount > 0) {
                    badge.style.display = 'inline-flex';
                    badge.innerText = pendingCount;
                } else {
                    badge.style.display = 'none';
                }
            }

            // Render list inside dropdown
            const listEl = document.getElementById('joinRequestsDropdownList');
            if (!listEl) return;

            if (incoming.length === 0 && outgoing.length === 0) {
                listEl.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem; padding:1.2rem; text-align:center;">No join requests at this time.</p>`;
                return;
            }

            let html = '';

            // Section 1: Incoming Join Requests (for projects created by this user)
            if (incoming.length > 0) {
                html += `
                    <div style="font-size:0.75rem; font-weight:700; color:#fbbf24; text-transform:uppercase; letter-spacing:0.5px; padding:0.2rem 0.4rem;">
                        Incoming Requests (${incoming.length})
                    </div>
                `;
                html += incoming.map(r => `
                    <div class="join-request-card unread">
                        <div style="font-weight:700; color:var(--text-main); font-size:0.88rem;">${this.escapeHtml(r.idea_title)}</div>
                        <div style="font-size:0.8rem; color:var(--text-muted);">
                            <strong>${this.escapeHtml(r.applicant_name)}</strong> (${r.applicant_dept || 'Student'}) requested to join your project.
                        </div>
                        <div style="display:flex; gap:0.4rem; margin-top:0.35rem; align-items:center;">
                            <button class="btn btn-sm btn-cyan" style="padding:0.25rem 0.65rem; font-size:0.75rem;" onclick="Teammates.respondJoin('${r.post_id}', '${r.applicant_id}', 'accept')">Accept</button>
                            <button class="btn btn-sm btn-secondary" style="padding:0.25rem 0.65rem; font-size:0.75rem;" onclick="Teammates.respondJoin('${r.post_id}', '${r.applicant_id}', 'reject')">Reject</button>
                            <button class="btn btn-sm btn-secondary" style="padding:0.25rem 0.65rem; font-size:0.75rem; margin-left:auto;" onclick="window.openDirectChat('${r.applicant_id}', '${this.escapeJs(r.applicant_name)}')">Message</button>
                        </div>
                    </div>
                `).join('');
            }

            // Section 2: Outgoing Requests (sent by this user)
            if (outgoing.length > 0) {
                html += `
                    <div style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; padding:0.4rem 0.4rem 0.2rem; margin-top:0.4rem;">
                        Your Sent Requests (${outgoing.length})
                    </div>
                `;
                html += outgoing.map(r => {
                    let statusPill = `<span style="color:#fbbf24; font-weight:600;">Pending Review</span>`;
                    if (r.status === 'Accepted') {
                        statusPill = `<span style="color:#10b981; font-weight:700;">Accepted</span>`;
                    } else if (r.status === 'Rejected') {
                        statusPill = `<span style="color:#ef4444; font-weight:600;">Declined</span>`;
                    }

                    return `
                        <div class="join-request-card">
                            <div style="font-weight:600; color:var(--text-main); font-size:0.85rem;">${this.escapeHtml(r.idea_title)}</div>
                            <div style="font-size:0.78rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;">
                                <span>Owner: ${this.escapeHtml(r.creator_name || 'Project Creator')}</span>
                                <span>${statusPill}</span>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            listEl.innerHTML = html;
        } catch (e) {
            console.error('Error fetching join requests', e);
        }
    },

    async respondJoin(postId, applicantId, action) {
        const user = this.getUser();
        if (!user || user.role !== 'Student') return;

        try {
            const res = await fetch('/api/projects/respond_join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    post_id: postId,
                    applicant_id: applicantId,
                    creator_id: user.user_id,
                    action: action
                })
            });
            const data = await res.json();
            alert(data.message);
            this.fetchJoinRequests();
            this.loadProjects();
        } catch (e) {
            console.error('Error responding to join request', e);
        }
    },

    // ── Project Board Rendering ──
    async loadProjects() {
        this.getUser();
        const user = this.currentUser;
        const userRole = user ? user.role : null;

        // Button visibility check
        const openBtn = document.getElementById('openPostProjectBtn');
        if (openBtn) {
            openBtn.style.display = (userRole === 'Student') ? 'inline-block' : 'none';
        }

        const container = document.getElementById('projectBoardContainer');
        if (!container) return;

        try {
            const res = await fetch('/api/projects/all');
            const data = await res.json();
            
            if (data.success && data.posts && data.posts.length > 0) {
                container.innerHTML = data.posts.map(p => {
                    const isCreator = user && (p.student_id === user.user_id);
                    const isMember = user && p.teammates && p.teammates.some(t => t.student_id === user.user_id);
                    const isPending = user && p.pending_requests && p.pending_requests.some(t => t.student_id === user.user_id);

                    // Build role-specific actions:
                    let actionHtml = '';

                    if (userRole === 'Student') {
                        if (isCreator) {
                            // Creator options: Single clean "Messages" button and "Delete"
                            actionHtml = `
                                <span style="font-size:0.85rem; color:var(--accent-indigo); font-weight:700; padding:0.3rem 0;">Your Project Post</span>
                                <button class="btn btn-sm btn-cyan" onclick="Teammates.openCreatorChat('${p.post_id}')">Messages</button>
                                <button class="btn btn-sm btn-danger" style="margin-left:auto;" onclick="Teammates.deleteProject('${p.post_id}')">Delete</button>
                            `;
                        } else if (isMember) {
                            // Accepted member: Can text creator
                            actionHtml = `
                                <span style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:#10b981; padding:0.35rem 0.7rem; border-radius:6px; font-weight:700; font-size:0.8rem; display:inline-flex; align-items:center;">
                                    Joined Team
                                </span>
                                <button class="btn btn-sm btn-cyan" onclick="window.openDirectChat('${p.student_id}', '${this.escapeJs(p.author_name)}')">Message Creator</button>
                            `;
                        } else if (isPending) {
                            // Pending applicant: Can text creator before being accepted
                            actionHtml = `
                                <button class="btn btn-sm btn-secondary" disabled style="opacity:0.85; cursor:not-allowed;">Join Request Pending</button>
                                <button class="btn btn-sm btn-cyan" onclick="window.openDirectChat('${p.student_id}', '${this.escapeJs(p.author_name)}')">Message Creator</button>
                            `;
                        } else {
                            // Student not yet requested: Can text creator or request to join
                            actionHtml = `
                                <button class="btn btn-sm btn-cyan" onclick="window.openDirectChat('${p.student_id}', '${this.escapeJs(p.author_name)}')">Message Creator</button>
                                <button class="btn btn-sm btn-secondary" onclick="Teammates.joinProject('${p.post_id}')">Request to Join</button>
                            `;
                        }
                    } else if (userRole === 'Admin') {
                        actionHtml = `
                            <span style="font-size:0.8rem; color:var(--text-muted);">Admin Moderation</span>
                            <button class="btn btn-sm btn-danger" style="margin-left:auto;" onclick="Teammates.deleteProject('${p.post_id}')">Delete Post</button>
                        `;
                    } else if (userRole === 'Faculty') {
                        actionHtml = `
                            <span style="font-size:0.8rem; color:var(--text-muted);">Faculty View Only</span>
                        `;
                    } else {
                        actionHtml = `
                            <span style="font-size:0.8rem; color:var(--text-muted);">Log in to collaborate</span>
                        `;
                    }

                    // Creator's pending join requests box on the card:
                    let pendingBoxHtml = '';
                    if (isCreator && p.pending_requests && p.pending_requests.length > 0) {
                        pendingBoxHtml = `
                            <div class="pending-join-requests-box">
                                <div style="font-weight:700; font-size:0.82rem; color:#fbbf24; margin-bottom:0.4rem;">
                                    Pending Join Requests (${p.pending_requests.length}):
                                </div>
                                ${p.pending_requests.map(req => `
                                    <div class="pending-join-item">
                                        <div>
                                            <strong>${this.escapeHtml(req.name)}</strong> (${req.department || 'Student'})
                                        </div>
                                        <div style="display:flex; gap:0.4rem;">
                                            <button class="btn btn-sm btn-cyan" style="padding:0.2rem 0.55rem; font-size:0.75rem;" onclick="Teammates.respondJoin('${p.post_id}', '${req.student_id}', 'accept')">Accept</button>
                                            <button class="btn btn-sm btn-secondary" style="padding:0.2rem 0.55rem; font-size:0.75rem;" onclick="Teammates.respondJoin('${p.post_id}', '${req.student_id}', 'reject')">Reject</button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    }

                    return `
                        <div class="project-card" id="project-post-${p.post_id}">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:0.5rem;">
                                <div class="project-title">${this.escapeHtml(p.idea_title)}</div>
                                <span class="role-pill role-Student" style="font-size:0.75rem;">Student Project</span>
                            </div>
                            <div class="project-meta">
                                Posted by <strong>${this.escapeHtml(p.author_name)}</strong> (${p.department || 'CSE'}) &bull; ${p.created_at}
                            </div>
                            <div class="project-desc">${this.escapeHtml(p.description)}</div>
                            <div class="skills-req">
                                ${(Array.isArray(p.required_skills) ? p.required_skills : []).map(s => `<span class="tag">${this.escapeHtml(s.trim())}</span>`).join('')}
                            </div>

                            ${(p.teammates && p.teammates.length > 0) ? `
                                <div style="margin-top:0.8rem; padding-top:0.6rem; border-top:1px solid var(--border-color); font-size:0.82rem; color:var(--text-muted);">
                                    <strong style="color:var(--text-main);">Team Members:</strong>
                                    <div style="display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.4rem;">
                                        ${p.teammates.map(t => `
                                            <span style="background:rgba(255,255,255,0.08); padding:0.25rem 0.6rem; border-radius:6px; font-size:0.8rem; color:#f1f5f9;">
                                                ${this.escapeHtml(t.name)}
                                            </span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${pendingBoxHtml}

                            <div style="display:flex; gap:0.6rem; margin-top:1rem; flex-wrap:wrap; align-items:center;">
                                ${actionHtml}
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = `<p style="color:var(--text-muted); padding:2rem; grid-column:1/-1; text-align:center;">No project ideas posted yet. Be the first!</p>`;
            }
        } catch (err) {
            console.error('Failed to load project posts', err);
            container.innerHTML = `<p style="color:var(--accent-pink); padding:2rem; text-align:center;">Error loading projects. Please refresh.</p>`;
        }
    },

    openCreatorChat(postId) {
        // Open chat with latest applicant or member, or open contact list
        fetch('/api/projects/all')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.posts) {
                    const p = data.posts.find(x => x.post_id === postId);
                    if (p) {
                        if (p.pending_requests && p.pending_requests.length > 0) {
                            const req = p.pending_requests[0];
                            return window.openDirectChat(req.student_id, req.name);
                        } else if (p.teammates && p.teammates.length > 0) {
                            const tm = p.teammates[0];
                            return window.openDirectChat(tm.student_id, tm.name);
                        }
                    }
                }
                // Fallback: fetch recent chat contacts
                const user = this.getUser();
                if (user) {
                    fetch(`/api/messages/contacts?user_id=${user.user_id}`)
                        .then(r => r.json())
                        .then(cData => {
                            if (cData.contacts && cData.contacts.length > 0) {
                                const c = cData.contacts[0];
                                window.openDirectChat(c.user_id, c.name);
                            } else {
                                alert('No messages or applicants yet for this project. When students text you or request to join, click Messages to chat with them.');
                            }
                        });
                }
            });
    },

    async deleteProject(postId) {
        const user = this.getUser();
        if (!user) return alert('Please log in.');
        if (!confirm('Are you sure you want to delete this project post?')) return;

        try {
            const res = await fetch('/api/projects/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ post_id: postId, user_id: user.user_id })
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                this.loadProjects();
            }
        } catch (err) {
            console.error('Delete project error', err);
        }
    },

    async submitProject() {
        const user = this.getUser();
        if (!user || user.role !== 'Student') {
            return alert('Only students can post project ideas in Teammate Finder.');
        }

        const title = document.getElementById('projTitle').value.trim();
        const desc = document.getElementById('projDesc').value.trim();
        const skills = document.getElementById('projSkills').value.trim();
        
        if (!title || !desc || !skills) {
            return alert('All fields are required.');
        }

        try {
            const res = await fetch('/api/projects/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    student_id: user.user_id,
                    user_id: user.user_id, 
                    idea_title: title, 
                    description: desc, 
                    required_skills: skills 
                })
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('postProjectModal')?.classList.remove('open');
                document.getElementById('postProjectForm')?.reset();
                this.loadProjects();
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error('Submit project error', err);
        }
    },

    async joinProject(postId) {
        const user = this.getUser();
        if (!user || user.role !== 'Student') {
            return alert('Only students can request to join project teams.');
        }

        try {
            const res = await fetch('/api/projects/join', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    student_id: user.user_id,
                    user_id: user.user_id, 
                    post_id: postId 
                })
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                this.loadProjects();
                this.fetchJoinRequests();
            }
        } catch (err) {
            console.error('Join project error', err);
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
