document.addEventListener('DOMContentLoaded', () => {
    // Auth elements
    const authOverlay = document.getElementById('auth-overlay');
    const authForm = document.getElementById('auth-form');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const authSubmit = document.getElementById('auth-submit');
    const emailGroup = document.getElementById('email-group');
    const authSwitchBtn = document.getElementById('auth-switch-btn');
    const authSwitchText = document.getElementById('auth-switch-text');
    
    // Auth state
    let isLoginMode = true;
    let token = localStorage.getItem('dc_token');
    let currentSessionId = null;

    // UI elements
    const historyList = document.getElementById('history-list');
    const chatContainer = document.getElementById('chat-container');
    const emptyState = document.getElementById('empty-state');
    const userDisplay = document.getElementById('user-display');
    const logoutBtn = document.getElementById('logout-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const compileForm = document.getElementById('compile-form');
    const chatInput = document.getElementById('chat-input');
    const fileInput = document.getElementById('file-upload-input');
    const fileIndicator = document.getElementById('file-indicator');

    // Utility headers
    function getHeaders() {
        return { 'Authorization': `Bearer ${token}` };
    }

    // Auth Swapping
    authSwitchBtn.addEventListener('click', () => {
        isLoginMode = !isLoginMode;
        if (isLoginMode) {
            authTitle.textContent = "Welcome Back";
            authSubtitle.textContent = "Log in to DocuCompiler to continue";
            authSubmit.textContent = "Log In";
            emailGroup.classList.add('hidden');
            document.getElementById('auth-email').required = false;
            authSwitchText.textContent = "Don't have an account?";
            authSwitchBtn.textContent = "Sign up";
            document.querySelector("label[for='auth-name']").textContent = "Username or Email";
        } else {
            authTitle.textContent = "Create an Account";
            authSubtitle.textContent = "Sign up to start summarizing";
            authSubmit.textContent = "Sign Up";
            emailGroup.classList.remove('hidden');
            document.getElementById('auth-email').required = true;
            authSwitchText.textContent = "Already have an account?";
            authSwitchBtn.textContent = "Log in";
            document.querySelector("label[for='auth-name']").textContent = "Username";
        }
    });

    // Handle Auth Submit
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('auth-name').value;
        const password = document.getElementById('auth-password').value;
        const formData = new FormData();
        formData.append('name', name);
        formData.append('password', password);
        
        if (!isLoginMode) {
            formData.append('email', document.getElementById('auth-email').value);
            try {
                const res = await fetch('/api/signup', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail);
                alert("Account created! Please log in.");
                authSwitchBtn.click();
            } catch(e) { alert(e.message); }
        } else {
            try {
                const res = await fetch('/api/login', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail);
                const data = await res.json();
                token = data.token;
                localStorage.setItem('dc_token', token);
                authForm.reset();
                checkAuth();
            } catch(e) { alert(e.message); }
        }
    });

    // Initial check
    async function checkAuth() {
        if (!token) {
            authOverlay.classList.remove('hidden');
            return;
        }
        try {
            const res = await fetch('/api/me', { headers: getHeaders() });
            if (!res.ok) throw new Error("Invalid token");
            const user = await res.json();
            userDisplay.textContent = user.name;
            authOverlay.classList.add('hidden');
            loadSessions();
        } catch(e) {
            localStorage.removeItem('dc_token');
            token = null;
            authOverlay.classList.remove('hidden');
        }
    }

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('dc_token');
        token = null;
        chatContainer.innerHTML = '';
        chatContainer.appendChild(emptyState);
        emptyState.classList.remove('hidden');
        authOverlay.classList.remove('hidden');
    });

    // Sessions Loading
    async function loadSessions() {
        try {
            const res = await fetch('/api/sessions', { headers: getHeaders() });
            const data = await res.json();
            historyList.innerHTML = '';
            data.forEach(s => {
                const dev = document.createElement('div');
                dev.className = 'history-item';
                if(s.id === currentSessionId) dev.classList.add('active');
                
                const span = document.createElement('span');
                span.textContent = s.title;
                dev.appendChild(span);

                const del = document.createElement('button');
                del.className = 'delete-btn';
                del.innerHTML = '&times;';
                del.onclick = async (e) => {
                    e.stopPropagation();
                    await fetch(`/api/sessions/${s.id}`, { method: 'DELETE', headers: getHeaders()});
                    if(currentSessionId === s.id) {
                        currentSessionId = null;
                        clearChat();
                    }
                    loadSessions();
                };
                dev.appendChild(del);

                dev.onclick = () => loadSessionHistory(s.id);
                historyList.appendChild(dev);
            });
        } catch(e) { console.error(e); }
    }

    async function loadSessionHistory(id) {
        currentSessionId = id;
        loadSessions(); 
        
        try {
            const res = await fetch(`/api/sessions/${id}`, { headers: getHeaders() });
            const history = await res.json();
            
            clearChat();
            if(history.length > 0) emptyState.classList.add('hidden');

            history.forEach(msg => {
                addChatBubble(msg.role, msg.content);
            });
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch(e) { console.error(e); }
    }

    newChatBtn.addEventListener('click', () => {
        currentSessionId = null;
        loadSessions();
        clearChat();
        emptyState.classList.remove('hidden');
    });

    function clearChat() {
        Array.from(chatContainer.children).forEach(c => {
            if(c !== emptyState) c.remove();
        });
    }

    function addChatBubble(role, content) {
        emptyState.classList.add('hidden');
        const d = document.createElement('div');
        d.className = `chat-bubble bubble-${role}`;
        d.innerHTML = content.replace(/\n/g, '<br>');
        chatContainer.appendChild(d);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Input Handling
    fileInput.addEventListener('change', () => {
        if(fileInput.files.length > 0) {
            fileIndicator.textContent = '📎 ' + fileInput.files[0].name;
            fileIndicator.style.background = '#e9d8fd';
            fileIndicator.style.color = '#553c9a';
        } else {
            fileIndicator.textContent = '📎 Attach File';
            fileIndicator.style.background = '#edf2f7';
            fileIndicator.style.color = '#718096';
        }
    });

    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    chatInput.addEventListener('keydown', (e) => {
        if(e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            compileForm.dispatchEvent(new Event('submit'));
        }
    });

    compileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const textValue = chatInput.value.trim();
        const hasFile = fileInput.files.length > 0;
        
        if (!textValue && !hasFile) return;
        
        let fd = new FormData();
        
        if(hasFile) {
            fd.append('file', fileInput.files[0]);
            if(textValue) fd.append('query', textValue);
        } else {
            fd.append('text', textValue);
        }
        
        fd.append('strategy', document.getElementById('strategy').value);
        fd.append('mode', document.getElementById('mode').value);
        if(currentSessionId) fd.append('session_id', currentSessionId);
        
        let userDisplayStr = textValue;
        if(hasFile) userDisplayStr = `[File attached: ${fileInput.files[0].name}]\n${textValue}`;
        if(!textValue && hasFile) userDisplayStr = `[File attached: ${fileInput.files[0].name}]`;
        
        addChatBubble('user', userDisplayStr);
        
        chatInput.value = '';
        chatInput.style.height = 'auto';
        if(hasFile) {
            fileInput.value = '';
            fileInput.dispatchEvent(new Event('change'));
        }

        const placeholder = document.createElement('div');
        placeholder.className = 'chat-bubble bubble-assistant';
        placeholder.innerHTML = '<i>Processing...</i>';
        chatContainer.appendChild(placeholder);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: getHeaders(),
                body: fd
            });
            const data = await response.json();
            if(!response.ok) throw new Error(data.detail);

            placeholder.remove();
            
            let answerText = data.summary;
            if(data.answer && data.answer !== "QA dependencies not installed.") {
                answerText += `\n\n**A:** ${data.answer}`;
            }
            
            if(!currentSessionId) {
                currentSessionId = data.session_id;
                loadSessions(); 
            }
            
            addChatBubble('assistant', answerText);
            
        } catch(err) {
            placeholder.remove();
            addChatBubble('assistant', 'Error: ' + err.message);
        }
    });

    checkAuth();
});
