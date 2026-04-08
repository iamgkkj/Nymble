// Core API calls
const API_BASE = '/api';

const state = {
    token: localStorage.getItem('nymble_token'),
    identity: null,
    challengeId: null,
    currentBoard: 'lobby'
};

// Distinct colors based on text hash
function getColor(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = text.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 80%, 65%)`; // Bright pastel for both modes
}

// DOM Elements
const views = {
    auth: document.getElementById('auth-view'),
    boards: document.getElementById('boards-view')
};

const captchaQ = document.getElementById('captcha-question');
const captchaOpts = document.getElementById('captcha-options');
const authError = document.getElementById('auth-error');
const themeToggle = document.getElementById('theme-toggle');

// INIT
document.addEventListener('DOMContentLoaded', async () => {
    setupThemeToggle();
    if (state.token) {
        // Assume valid, could verify via a new endpoint or just try fetching boards
        showView('boards');
        initBoardsView();
    } else {
        showView('auth');
        loadCaptcha();
    }
});

function showView(viewName) {
    Object.values(views).forEach(v => {
        v.classList.remove('active');
        setTimeout(() => v.classList.add('hidden'), 400); // Wait for fade out
    });
    
    setTimeout(() => {
        views[viewName].classList.remove('hidden');
        // Small delay to allow display to apply before opacity transition
        requestAnimationFrame(() => views[viewName].classList.add('active'));
    }, 450);
}

function setupThemeToggle() {
    const isLight = localStorage.getItem('theme') === 'light';
    if (isLight) document.body.classList.add('light-theme');
    
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
    });
}

// -- CAPTCHA FLOW --
async function loadCaptcha() {
    try {
        const res = await fetch(`${API_BASE}/captcha`);
        const data = await res.json();
        captchaQ.innerText = data.question;
        state.challengeId = data.challenge_id;
        
        captchaOpts.innerHTML = '';
        data.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'glass-btn emoji-btn';
            btn.innerText = opt;
            btn.onclick = () => submitCaptcha(opt);
            captchaOpts.appendChild(btn);
        });
    } catch(e) {
        captchaQ.innerText = "Error loading secure gateway. Refresh the page.";
    }
}

async function submitCaptcha(answer) {
    authError.classList.add('hidden');
    
    // Disable buttons
    const btns = captchaOpts.querySelectorAll('button');
    btns.forEach(b => b.disabled = true);
    
    try {
        const res = await fetch(`${API_BASE}/verify-captcha`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ solution: answer, challenge_id: state.challengeId })
        });
        const data = await res.json();
        
        if (res.ok) {
            state.token = data.token;
            state.identity = data.identity;
            localStorage.setItem('nymble_token', data.token);
            
            showView('boards');
            initBoardsView();
        } else {
            authError.innerText = data.detail || 'Incorrect answer.';
            authError.classList.remove('hidden');
            loadCaptcha(); // load new one
        }
    } catch(e) {
        authError.innerText = 'Network error. Try again.';
        authError.classList.remove('hidden');
        btns.forEach(b => b.disabled = false);
    }
}

// -- BOARDS FLOW --
async function initBoardsView() {
    // If we have token but missed getting identity (reload) we can fetch it via /api/me
    if (!state.identity && state.token) {
        try {
            const res = await fetch(`${API_BASE}/me`, { headers: { 'X-Session-Token': state.token } });
            if (res.ok) {
                const data = await res.json();
                state.identity = data.username;
            }
        } catch(e) {}
    }
    
    document.getElementById('user-identity').innerText = state.identity || "Connected";
    
    // Setup Profile badge click for Token copy / continue session
    const badge = document.querySelector('.identity-badge');
    badge.onclick = () => {
        prompt("Save this Token securely to restore your session or chats anywhere:", state.token);
    };
    
    // Initialize WebSockets for Private chat
    initChat();
    
    loadBoards();
    loadInbox();
}

async function loadBoards() {
    try {
        const res = await fetch(`${API_BASE}/boards`, {
            headers: { 'X-Session-Token': state.token }
        });
        const boards = await res.json();
        
        const list = document.getElementById('board-list');
        list.innerHTML = '';
        boards.forEach((b, i) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="hash">#</span>${b.name}`;
            
            // Color each board distinctly
            const boardColor = getColor(b.name);
            li.style.setProperty('--board-color', boardColor);
            
            if (i === 0) {
                li.classList.add('active');
                state.currentBoard = b.name;
            }
            li.addEventListener('click', () => {
                document.querySelectorAll('#board-list li').forEach(el=>el.classList.remove('active'));
                li.classList.add('active');
                state.currentBoard = b.name;
                
                document.getElementById('feed-container').classList.remove('hidden');
                document.getElementById('inbox-container').classList.add('hidden');
                
                loadFeed(b.name);
            });
            list.appendChild(li);
        });
        
        if (boards.length > 0) {
            loadFeed(boards[0].name);
        }
    } catch(e) {
        console.error("Failed to load boards", e);
    }
}

async function loadInbox() {
    try {
        const res = await fetch(`${API_BASE}/chats`, { headers: { 'X-Session-Token': state.token } });
        const listContainer = document.getElementById('inbox-list');
        listContainer.innerHTML = '';
        
        if (res.ok) {
            const inbox = await res.json();
            if (inbox.length === 0) {
                listContainer.innerHTML = `<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No inboxes found.</p>`;
            } else {
                inbox.forEach(user => {
                    const d = document.createElement('div');
                    d.className = 'glass-panel';
                    d.style.padding = '1rem';
                    d.style.cursor = 'pointer';
                    d.style.display = 'flex';
                    d.style.justifyContent = 'space-between';
                    d.innerHTML = `<h3 style="color:${getColor(user.username)}">${user.username}</h3> <span class="chat-icon">💬</span>`;
                    d.onclick = () => openChat(user.username);
                    listContainer.appendChild(d);
                });
            }
        }
    } catch(e) {
        console.error(e);
    }
}

async function loadFeed(boardName) {
    const container = document.getElementById('posts-container');
    container.innerHTML = '<div class="glass-panel skeleton-loader"><p>Loading feeds...</p></div>';
    
    try {
        const res = await fetch(`${API_BASE}/boards/${boardName}/posts`, {
            headers: { 'X-Session-Token': state.token }
        });
        const posts = await res.json();
        
        container.innerHTML = '';
        if (posts.length === 0) {
            container.innerHTML = '<div class="glass-panel" style="padding: 2rem; text-align: center;"><p>No posts here yet. Be the first!</p></div>';
            return;
        }
        
        posts.forEach((p, idx) => {
            const card = document.createElement('div');
            // Basic glowing left border matching index
            const colorClass = `color-${(idx % 5) + 1}`; 
            card.className = `glass-panel post-card ${colorClass}`;
            
            let contentHtml = `<p class="post-text">${p.content}</p>`;
            if (p.is_whisper) {
                contentHtml = `<p class="post-text whisper-text"><span class="whisper-label">❈ Whisper</span> <span class="blurred">${p.content}</span></p>`;
            }
            
            // Distinguish username with a robust color
            const authorColor = getColor(p.author_name);
            
            // Add message icon if not current user
            const chatIcon = p.author_name !== state.identity 
                ? `<span class="chat-icon tooltip" data-tip="Start a private chat">💬</span>` 
                : `<span class="chat-icon my-icon tooltip" data-tip="This is you">👤</span>`;
            
            card.innerHTML = `
                <div class="post-header">
                    <div class="post-author-wrapper">
                        <span class="post-author" style="color: ${authorColor}">${p.author_name}</span>
                        ${chatIcon}
                    </div>
                    <span class="post-time">${new Date(p.created_at).toLocaleString([], {hour: '2-digit', minute:'2-digit', month:'numeric', day:'numeric'})}</span>
                </div>
                <div class="post-body">
                    ${contentHtml}
                    ${p.image_url ? `<img src="${p.image_url}" class="post-image" />` : ''}
                </div>
            `;
            
            card.querySelector('.chat-icon').onclick = () => {
                if (p.author_name !== state.identity) openChat(p.author_name);
            };
            
            container.appendChild(card);
        });
    } catch(e) {
        container.innerHTML = '<div class="glass-panel" style="padding: 2rem; color: #ff4a4a;"><p>Error loading posts.</p></div>';
    }
}

// POST BUTTON LISTENER
document.getElementById('btn-post').addEventListener('click', async () => {
    const textInput = document.getElementById('composer-text');
    const whisperToggle = document.getElementById('composer-whisper');
    
    const text = textInput.value.trim();
    if (!text) return;
    
    const fd = new FormData();
    fd.append("content", text);
    fd.append("is_whisper", whisperToggle.checked);
    
    try {
        const res = await fetch(`${API_BASE}/boards/${state.currentBoard}/posts`, {
            method: 'POST',
            headers: { 'X-Session-Token': state.token },
            body: fd
        });
        if (res.ok) {
            textInput.value = '';
            whisperToggle.checked = false;
            loadFeed(state.currentBoard);
        } else {
            const err = await res.json();
            alert("Error posting: " + (err.detail || "Unknown"));
        }
    } catch (e) {
        console.error("Failed to post:", e);
    }
});

// -- CHAT LOGIC --
let chatSocket = null;
let activeChatUser = null;
const chatOverlay = document.getElementById('chat-overlay');
const chatMsgs = document.getElementById('chat-messages');

function initChat() {
    const wsUrl = `ws://${window.location.host}/ws/chat/${state.token}`;
    chatSocket = new WebSocket(wsUrl);
    
    chatSocket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        // incoming format: {from: username, content: string, status: string, to: string}
        
        if (msg.status === "sent") {
            // Echo back of our own message
            if (activeChatUser === msg.to) {
                appendChatMessage(msg.content, true);
            }
        } else if (msg.error) {
            alert(`Chat Error: ${msg.error}`);
        } else {
            // Received a personal message!
            if (chatOverlay.classList.contains('chat-hidden') || activeChatUser !== msg.from) {
                const w = document.createElement('div');
                w.className = 'glass-panel';
                w.style.position = 'fixed'; w.style.top = '2rem'; w.style.left = '50%'; w.style.transform = 'translateX(-50%)'; w.style.zIndex='9999'; w.style.padding='1rem'; w.style.cursor='pointer';
                w.innerHTML = `<strong style="color:var(--accent-glow)">${msg.from}</strong> sent you a secure ping: "${msg.content.substring(0,20)}..."`;
                w.onclick = () => { w.remove(); openChat(msg.from); };
                document.body.appendChild(w);
                setTimeout(() => w.remove(), 6000);
            } else {
                appendChatMessage(msg.content, false);
            }
        }
    };
    
    chatSocket.onclose = () => {
        setTimeout(() => { if (state.token) initChat(); }, 5000);
    };
}

async function openChat(username) {
    activeChatUser = username;
    document.getElementById('chat-target-user').innerText = username;
    chatMsgs.innerHTML = '';
    
    // Load historical messages from API
    try {
        const res = await fetch(`${API_BASE}/chats/${username}`, { headers: {'X-Session-Token': state.token} });
        if (res.ok) {
            const history = await res.json();
            if (history.length > 0) {
                history.forEach(m => {
                    appendChatMessage(m.content, m.from === state.identity);
                });
            } else {
                appendChatMessage(`Connected via secure socket to ${username}. Say hi!`, false);
            }
        }
    } catch(e) {
        console.error(e);
        appendChatMessage(`Connected via secure socket to ${username}.`, false);
    }
    
    chatOverlay.classList.remove('chat-hidden');
    
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
        initChat();
    }
}

document.getElementById('close-chat').onclick = () => {
    chatOverlay.classList.add('chat-hidden');
    activeChatUser = null;
};

document.getElementById('new-chat-btn').onclick = () => {
    // Show Inbox view instead of feed!
    document.getElementById('feed-container').classList.add('hidden');
    document.getElementById('inbox-container').classList.remove('hidden');
    loadInbox();
};

document.getElementById('btn-start-chat').onclick = () => {
    const input = document.getElementById('new-chat-input');
    const target = input.value.trim();
    if (target) {
        openChat(target);
        input.value = '';
    }
};

document.getElementById('btn-send-chat').onclick = () => {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || !activeChatUser) return;
    
    chatSocket.send(JSON.stringify({
        to: activeChatUser,
        content: text,
        is_whisper: false
    }));
    input.value = '';
};

document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') document.getElementById('btn-send-chat').click();
});

function appendChatMessage(content, isSent) {
    const d = document.createElement('div');
    d.className = `chat-bubble ${isSent ? 'sent' : 'received'}`;
    d.textContent = content; // secure against XSS
    chatMsgs.appendChild(d);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
}
