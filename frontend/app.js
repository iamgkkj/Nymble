// Core API calls
const API_BASE = '/api';

const state = {
    token: localStorage.getItem('nymble_token'),
    identity: null,
    captchaSalt: null,
    currentBoard: 'lobby'
};

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
    // For now, hardcode lobby board in UI mock until we fetch from actual endpoint
    document.getElementById('user-identity').innerText = state.identity || "Connected Identity";
    loadBoards();
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
            li.innerText = `#${b.name}`;
            if (i === 0) {
                li.classList.add('active');
                state.currentBoard = b.name;
                // We would load post feeds here
            }
            li.addEventListener('click', () => {
                document.querySelectorAll('#board-list li').forEach(el=>el.classList.remove('active'));
                li.classList.add('active');
                state.currentBoard = b.name;
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
            // Give it a random colorful glow class (color-1 through color-5)
            const colorClass = `color-${(idx % 5) + 1}`; 
            card.className = `glass-panel post-card ${colorClass}`;
            
            let contentHtml = `<p class="post-text">${p.content}</p>`;
            if (p.is_whisper) {
                contentHtml = `<p class="post-text whisper-text"><em>[Whisper]</em> <span class="blurred">${p.content}</span></p>`;
            }
            
            card.innerHTML = `
                <div class="post-header">
                    <span class="post-author">${p.author_name}</span>
                    <span class="post-time">${new Date(p.created_at).toLocaleString()}</span>
                </div>
                <div class="post-body">
                    ${contentHtml}
                    ${p.image_url ? `<img src="${p.image_url}" class="post-image" />` : ''}
                </div>
            `;
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
