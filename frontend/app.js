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
const captchaAns = document.getElementById('captcha-answer');
const authError = document.getElementById('auth-error');
const btnSubmitCaptcha = document.getElementById('btn-submit-captcha');
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
        const res = await fetch(`${API_BASE}/auth/captcha`);
        const data = await res.json();
        captchaQ.innerText = data.question;
        state.captchaSalt = data.salt;
    } catch(e) {
        captchaQ.innerText = "Error loading secure gateway. Refresh the page.";
    }
}

btnSubmitCaptcha.addEventListener('click', async () => {
    const answer = captchaAns.value.trim();
    if (!answer) return;
    
    authError.classList.add('hidden');
    const oldHtml = btnSubmitCaptcha.innerHTML;
    btnSubmitCaptcha.innerHTML = 'Verifying...';
    
    try {
        const res = await fetch(`${API_BASE}/auth/verify-captcha`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ answer, salt: state.captchaSalt })
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
            captchaAns.value = '';
        }
    } catch(e) {
        authError.innerText = 'Network error. Try again.';
        authError.classList.remove('hidden');
    } finally {
        btnSubmitCaptcha.innerHTML = oldHtml;
    }
});

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
                // Load feed...
            });
            list.appendChild(li);
        });
    } catch(e) {
        console.error("Failed to load boards", e);
    }
}
