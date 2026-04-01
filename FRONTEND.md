# FRONTEND DOCUMENTATION

This document covers all the frontend files responsible for the UI/UX of DocuCompiler.

## List of Frontend Files
1. `static/index.html` - The structural skeleton of the app.
2. `static/style.css` - The visual styling, layout, and animations.
3. `static/script.js` - The dynamic logic handling user interactions and API calls to the backend.

---

## 1. `static/index.html`

### Purpose and UI/UX Role
This file is the single-page application (SPA) entry point. It creates the ChatGPT-like interface layout consisting of:
- An **Authentication Overlay** (for Login/Signup).
- A **Sidebar** (for showing chat history/sessions).
- A **Main Chat Area** (for displaying messages and summaries).
- An **Input Area** (for pasting text, attaching files, and setting strategies).

### How it Connects to the Backend
It doesn't directly connect to the backend logic itself, but it loads `script.js` which makes REST calls (`/api/login`, `/api/summarize`) and dynamically manipulates this HTML DOM.

### Line-by-Line Code Explanation

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Yeh basic HTML structure aur viewport setting hai (mobile par theek dikhne ke liye) -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuCompiler | Intelligent Summarization</title>
    
    <!-- Google Fonts se 'Inter' font load kar rahe hain -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    
    <!-- Custom CSS file ko link kar rahe hain -->
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <!-- Auth Overlay (Login/Signup box) jo default hidden nahi hota, JS ke through zarurat padne par hide/show hota hai -->
    <div id="auth-overlay" class="auth-overlay hidden">
        <div class="auth-box">
            <h2 id="auth-title">Welcome Back</h2>
            <p id="auth-subtitle">Log in to DocuCompiler to continue</p>
            
            <!-- Login/Signup form -->
            <form id="auth-form">
                <div class="input-group">
                    <label for="auth-name">Username or Email</label>
                    <input type="text" id="auth-name" required>
                </div>
                
                <!-- Email field (sirf Signup ke time show hota hai) -->
                <div id="email-group" class="input-group hidden">
                    <label for="auth-email">Email</label>
                    <input type="email" id="auth-email">
                </div>
                
                <div class="input-group">
                    <label for="auth-password">Password</label>
                    <input type="password" id="auth-password" required>
                </div>
                
                <button type="submit" class="btn-primary" id="auth-submit">Log In</button>
            </form>
            
            <!-- Login se Signup switch karne ka toggle -->
            <div class="auth-switch">
                <span id="auth-switch-text">Don't have an account?</span> 
                <a id="auth-switch-btn">Sign up</a>
            </div>
        </div>
    </div>

    <!-- Main App Layout (ChatGPT Style Interface) -->
    <div class="app-container">
        
        <!-- Sidebar: Purane chats/sessions dikhane ke liye -->
        <aside class="sidebar">
            <button class="new-chat-btn" id="new-chat-btn">+ New Document / Chat</button>
            
            <!-- Yahan JavaScript dynamcially purane chat items add karega -->
            <div class="history-list" id="history-list"></div>
            
            <div class="sidebar-footer">
                <!-- Logged in user ka naam yahan show hoga -->
                <span id="user-display">Loading...</span>
                <button class="logout-btn" id="logout-btn">Log out</button>
            </div>
        </aside>

        <!-- Main Chat Area: User aur AI ki conversation -->
        <main class="chat-area">
            <div class="chat-history-container" id="chat-container">
                
                <!-- Jab koi chat na ho toh yeh welcome message dikhega -->
                <div class="empty-state" id="empty-state">
                    <h1>DocuCompiler</h1>
                    <p>Select a history session, or paste text, upload a document, and ask questions below.</p>
                </div>
                <!-- Chat bubbles JS ke through yahan append honge -->
            </div>

            <!-- Input Area: Niche ka dabba jahan user type karta hai -->
            <div class="input-area">
                <form id="compile-form" class="input-container">
                    <div class="row">
                        <textarea id="chat-input" placeholder="Paste document text or question..."></textarea>
                    </div>
                    
                    <div class="row control-row">
                        <!-- File Upload ka custom button -->
                        <div class="file-input-wrapper">
                            <div class="file-btn" id="file-indicator">📎 Attach File</div>
                            <input type="file" id="file-upload-input" accept=".pdf,.docx,.txt">
                        </div>
                        
                        <button type="submit" class="send-btn" id="send-btn">Send / Compile</button>
                    </div>
                    
                    <!-- Settings Row (Strategy aur Format options) -->
                    <div class="settings-row">
                        <div class="options">
                            <label for="strategy">Strategy:</label>
                            <select id="strategy">
                                <option value="conservative">Conservative</option>
                                <option value="moderate" selected>Moderate</option>
                                <option value="aggressive">Aggressive</option>
                            </select>
                            
                            <label for="mode" style="margin-left: 1rem;">Format:</label>
                            <select id="mode">
                                <option value="paragraph" selected>Paragraph</option>
                                <option value="bullet">Bullet</option>
                            </select>
                        </div>
                    </div>
                </form>
            </div>
        </main>
    </div>

    <!-- Ant mein JavaScript file load ki -->
    <script src="/static/script.js"></script>
</body>
</html>
```

---

## 2. `static/style.css`

### Purpose and UI/UX Role
Provides a premium, "glassmorphic", dynamic aesthetic. Uses variables (`:root`) to handle theme colors easily.

### How it Connects to Backend
Aesthetics only. No backend connection.

### Core Highlights Explained
```css
/* Glassmorphism Effect: Auth box ko transparent aur blur effect deta hai */
.auth-box {
    background: var(--glass-bg); /* Semi-transparent safaid rang */
    backdrop-filter: blur(12px); /* Background ko dhundla (blur) karta hai */
    border-radius: 24px;         /* Gol kinare (rounded corners) */
}

/* Chat Input Textarea: Auto-resize ke liye styling */
.input-container textarea {
    width: 100%;
    border: none;
    background: transparent;
    resize: none; /* User manually resize na kar sake */
}
```

---

## 3. `static/script.js`

### Purpose and UI/UX Role
This is the brain of the frontend. It handles State Management (token, session ID), Form Submissions, API Fetching, and DOM UI Updates.

### How it Connects to Backend
Makes HTTP `fetch` requests to FastAPI endpoints (`/api/login`, `/api/summarize`, etc.) using JWT Bearer tokens for authentication and `FormData` for file uploads.

### Line-by-Line Code Explanation

```javascript
// Jab HTML document poori tarah load ho jaye, tab yeh code chale
document.addEventListener('DOMContentLoaded', () => {

    // ✅ HTML elements ko IDs ke zariye pakad rahe hain
    const authOverlay = document.getElementById('auth-overlay');
    const authForm = document.getElementById('auth-form');
    // ... basic DOM selections (authTitle, historyList, chatContainer, chatInput etc.)
    
    // Auth State variables store kar rahe hain
    let isLoginMode = true; // By default login screen dikhayenge
    let token = localStorage.getItem('dc_token'); // Browser memory se purana token nikalenge
    let currentSessionId = null; // Abhi konsa chat open hai, null matlab "New Chat"

    // ✅ API request bhejte waqt Token attach karne ka function
    function getHeaders() {
        return { 'Authorization': `Bearer ${token}` }; // Token ko Bearer string mein daal ke bhejenge
    }

    // ✅ Login aur Signup screen ko switch (toggle) karne ka event
    authSwitchBtn.addEventListener('click', () => {
        isLoginMode = !isLoginMode; // Mode ulta kar diya (login -> signup)
        
        if (isLoginMode) {
            // Agar login mode par aaye hain toh text change karo aur email field chupao
            authTitle.textContent = "Welcome Back";
            authSubmit.textContent = "Log In";
            emailGroup.classList.add('hidden'); // Email chhup gaya
        } else {
            // Agar signup mode par aaye hain toh naya text lagao aur email field dikhao
            authTitle.textContent = "Create an Account";
            authSubmit.textContent = "Sign Up";
            emailGroup.classList.remove('hidden'); // Email dikh gaya
        }
    });

    // ✅ Form submit hone par API Call (Login ya Signup)
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Page refresh hone se rokhta hai
        
        // Form ka data FormData object mein dalna
        const formData = new FormData();
        formData.append('name', document.getElementById('auth-name').value);
        formData.append('password', document.getElementById('auth-password').value);
        
        if (!isLoginMode) {
            // == SIGNUP LOGIC ==
            formData.append('email', document.getElementById('auth-email').value);
            try {
                // Backend ke /api/signup route par POST request bheji
                const res = await fetch('/api/signup', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail);
                
                alert("Account created! Please log in.");
                authSwitchBtn.click(); // Wapis login page par switch kar diya
            } catch(e) { alert(e.message); } // Error aaye toh alert karo
        } else {
            // == LOGIN LOGIC ==
            try {
                // Backend ke /api/login route par POST request bheji
                const res = await fetch('/api/login', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail);
                
                // Login successful! Token ko local storage mein save kar diya
                const data = await res.json();
                token = data.token;
                localStorage.setItem('dc_token', token);
                
                authForm.reset(); 
                checkAuth(); // Token check karke app mein enter karwao
            } catch(e) { alert(e.message); }
        }
    });

    // ✅ User authentication / Profile details check karne ka function
    async function checkAuth() {
        if (!token) {
            // Agar token nahi hai toh login popup dikhao
            authOverlay.classList.remove('hidden');
            return;
        }
        try {
            // User ki profile laney ke liye /api/me request 
            const res = await fetch('/api/me', { headers: getHeaders() });
            if (!res.ok) throw new Error("Invalid token");
            
            const user = await res.json();
            userDisplay.textContent = user.name; // Sidebar mein naam dikhao
            authOverlay.classList.add('hidden'); // Login popup chhupa do
            
            loadSessions(); // Login hote hi sidebar mein purani chats load karo
        } catch(e) {
            // Token expire ya invalid ho gaya
            localStorage.removeItem('dc_token');
            token = null;
            authOverlay.classList.remove('hidden');
        }
    }

    // ✅ Purani chats (sessions) sidebar mein dikhane ke liye API call
    async function loadSessions() {
        try {
            const res = await fetch('/api/sessions', { headers: getHeaders() });
            const data = await res.json();
            historyList.innerHTML = ''; // Pehle list clear karo
            
            // Har session ke liye ek naya item bana ke sidebar mein append karo
            data.forEach(s => {
                const dev = document.createElement('div');
                dev.className = 'history-item';
                
                // Agar yeh wahi session hai jo abhi load hai toh use highlight karo
                if(s.id === currentSessionId) dev.classList.add('active');
                
                dev.innerHTML = `<span>${s.title}</span>`; // Chat ka Title set kiya
                dev.onclick = () => loadSessionHistory(s.id); // Click hone par purani chat khule
                
                historyList.appendChild(dev);
            });
        } catch(e) { console.error(e); }
    }

    // ✅ Jab koi purani chat kholte hain toh uski history load karna
    async function loadSessionHistory(id) {
        currentSessionId = id;
        loadSessions(); // Highlight ko update karne ke liye
        
        try {
            const res = await fetch(`/api/sessions/${id}`, { headers: getHeaders() });
            const history = await res.json();
            
            clearChat(); // Pehle se dikh rahi chat hatao
            emptyState.classList.add('hidden'); // Welcome text chhupao

            // Database se aayi saari history screen par paint karna loop chala ke
            history.forEach(msg => {
                addChatBubble(msg.role, msg.content);
            });
        } catch(e) { console.error(e); }
    }

    // ✅ Naya chat bubble (UI block) add karna
    function addChatBubble(role, content) {
        emptyState.classList.add('hidden');
        const d = document.createElement('div');
        // Role = "user" (hamara bubble) or "assistant" (AI ka bubble)
        d.className = `chat-bubble bubble-${role}`; 
        
        // Text mein line breaks ko HTML ki <br> tags mein badalna
        d.innerHTML = content.replace(/\n/g, '<br>');
        
        chatContainer.appendChild(d); // Screen par append kiya
        chatContainer.scrollTop = chatContainer.scrollHeight; // Auto scroll to bottom
    }

    // ✅ Main logic: File/Text bhejna aur Summary/Answer fetch karna
    compileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const textValue = chatInput.value.trim();
        const hasFile = fileInput.files.length > 0;
        
        if (!textValue && !hasFile) return; // Kuch type nahi kiya toh kuch mat karo
        
        // Data bhejne ke liye FormData banaya kyonki file bhi upload ho sakti hai
        let fd = new FormData();
        
        if(hasFile) {
            fd.append('file', fileInput.files[0]);
            if(textValue) fd.append('query', textValue); // Agar text bhi hai toh woh question ban gaya
        } else {
            fd.append('text', textValue);
        }
        
        // Settings bhejna (Moderate, Paragraph etc.)
        fd.append('strategy', document.getElementById('strategy').value);
        fd.append('mode', document.getElementById('mode').value);
        
        // Agar pehle se chat khuli hai, toh uska ID bhejo taaki wahi save ho
        if(currentSessionId) fd.append('session_id', currentSessionId);
        
        // User ka message UI pe print karna
        addChatBubble('user', textValue || `[File attached: ${fileInput.files[0].name}]`);
        
        chatInput.value = ''; // Input box khali kar diya
        
        // Ek fake "Processing..." ka bubble dikhana AI aane se pehle
        const placeholder = document.createElement('div');
        placeholder.className = 'chat-bubble bubble-assistant';
        placeholder.innerHTML = '<i>Processing...</i>';
        chatContainer.appendChild(placeholder);

        try {
            // Main backend Summarize/QA API call 
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: getHeaders(), // Auth Token 
                body: fd               // Text and File Data
            });
            const data = await response.json();
            
            placeholder.remove(); // "Processing..." wala message hata do
            
            // AI ka answer aur summary format karke screen pe print karna
            let answerText = data.summary;
            if(data.answer) answerText += `\n\n**A:** ${data.answer}`;
            
            if(!currentSessionId) {
                // Agar naya chat tha, toh server se naya session ID mila, usey save karo
                currentSessionId = data.session_id; 
                loadSessions(); // Sidebar update karo
            }
            
            addChatBubble('assistant', answerText); // AI ka answer User ko dikha diya
            
        } catch(err) {
            placeholder.remove(); // Processing msg hatao
            addChatBubble('assistant', 'Error: ' + err.message); // Error dikhayein
        }
    });

    // Page start load hote hi sabse pehle Auth Check karo
    checkAuth();
});
```
