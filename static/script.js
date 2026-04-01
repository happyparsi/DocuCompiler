// Jab pura web page (HTML) load ho tab ye function chalega taki UI k control ko handle krske
document.addEventListener('DOMContentLoaded', () => {
    
    // --- AUTHENTICATION (LOGIN/SIGNUP) ELEMENTS KO HTML SE JS ME LANA ---
    const authOverlay = document.getElementById('auth-overlay'); // Login popup ki puri window
    const authForm = document.getElementById('auth-form'); // Login/Signup ka form data
    const authTitle = document.getElementById('auth-title'); // Popup ke upar heading 'Welcome Back'
    const authSubtitle = document.getElementById('auth-subtitle'); // Chota sa descriptive text
    const authSubmit = document.getElementById('auth-submit'); // Submit karne ka bada Button
    const emailGroup = document.getElementById('email-group'); // Email likhne wala dabba (hidden in login)
    const authSwitchBtn = document.getElementById('auth-switch-btn'); // Login se Signup banane wala chota link
    const authSwitchText = document.getElementById('auth-switch-text'); // Link k peeche likha "Don't have an account?"
    
    // --- APP STATE BANA RAHE HAIN (VARIABLES) ---
    let isLoginMode = true; // By default hum chahte hain user 'Login' page dekhay
    let token = localStorage.getItem('dc_token'); // Browser ki memory se purana chora hua Token dhoonda (agar hai toh)
    let currentSessionId = null; // Abhi user konsi chat par betha hy (Naye chat par None hoga!)

    // --- MAIN CHAT UI ELEMENTS KO HTML SE JS ME LANA ---
    const historyList = document.getElementById('history-list'); // Sidebar ke andr purani chats ki List
    const chatContainer = document.getElementById('chat-container'); // Jaha sabse zyada Messages (Bubbles) nazar ayenge
    const emptyState = document.getElementById('empty-state'); // Jab chat khali ho tou jo 'DocuCompiler' likha ara h
    const userDisplay = document.getElementById('user-display'); // Sidebar mein neechay jo naam hy idher
    const logoutBtn = document.getElementById('logout-btn'); // Logout button
    const newChatBtn = document.getElementById('new-chat-btn'); // "New Document / Chat" dbaane wala + button
    const compileForm = document.getElementById('compile-form'); // Neeche jidher Message, File, or button hai wo Form
    const chatInput = document.getElementById('chat-input'); // Bara dabba jismen Type kia jaye
    const fileInput = document.getElementById('file-upload-input'); // File chun_ne ka hidden input
    const fileIndicator = document.getElementById('file-indicator'); // File chuni hui hy tou '📎 my_file.pdf' ye dikhata hy

    // --- UTILITY/HELPER FUNCTION ---
    // Jab Backend ko API request bhejni ho, toh ye Token Headrs me daal ke bhejenge (Taakey backend pehchan ley user ko!)
    function getHeaders() {
        return { 'Authorization': `Bearer ${token}` }; 
    }

    // --- LOGIN AUR SIGNUP FORM SWITCH KARNA ---
    authSwitchBtn.addEventListener('click', () => {
        isLoginMode = !isLoginMode; // Mode ko ulta kardo. True hai tou False, False ha tou True!
        
        if (isLoginMode) {
            // Agar Login page par wapas aagaya hy 
            authTitle.textContent = "Welcome Back";
            authSubtitle.textContent = "Log in to DocuCompiler to continue";
            authSubmit.textContent = "Log In"; // Button ka text "Log In" kardia
            emailGroup.classList.add('hidden'); // Email box chupaa diya
            document.getElementById('auth-email').required = false; // Email zruri b mt rakho
            authSwitchText.textContent = "Don't have an account?";
            authSwitchBtn.textContent = "Sign up";
            document.querySelector("label[for='auth-name']").textContent = "Username or Email"; // Label wapis theem kardi
        } else {
            // Agar Signup (Naya account bananay) ke safhay pe he
            authTitle.textContent = "Create an Account";
            authSubtitle.textContent = "Sign up to start summarizing";
            authSubmit.textContent = "Sign Up"; // Btan ka text badal diya
            emailGroup.classList.remove('hidden'); // Email wale dabbe ka display Hidden mita dia
            document.getElementById('auth-email').required = true; // Email fill krna lazmi hai ab!
            authSwitchText.textContent = "Already have an account?";
            authSwitchBtn.textContent = "Log in";
            document.querySelector("label[for='auth-name']").textContent = "Username";
        }
    });

    // --- FORM (LOGIN/SIGNUP) SUBMIT HONE PAR ACTION ---
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Browser ka "page reload" hone wala by default behavior maar do!
        
        // Form ka data uthaya inputs dabbo se
        const name = document.getElementById('auth-name').value;
        const password = document.getElementById('auth-password').value;
        
        // Data bhejne ke lye format set kia (FormData backend easily pr leta hai file ki taran)
        const formData = new FormData();
        formData.append('name', name);
        formData.append('password', password);
        
        if (!isLoginMode) { // Agar Register kra rha tha ?
            formData.append('email', document.getElementById('auth-email').value);
            try {
                // Post request bheji Server API "/api/signup" pr
                const res = await fetch('/api/signup', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail); // Backend se error aay tou Exception Throw kro!
                
                alert("Account created! Please log in."); // Browser me OK PopUp dekr btaya Account ban gaya
                authSwitchBtn.click(); // Autmatically click daba ke Login walay Mode me laye user ko
            } catch(e) { alert(e.message); } // Koi bhi bura khail ho tou popup e.message bata dy ga!
        } else { // Agar bs normal Login he hy tou
            try {
                // Backend API ko POST ki 
                const res = await fetch('/api/login', { method: 'POST', body: formData });
                if (!res.ok) throw new Error((await res.json()).detail);
                
                const data = await res.json();
                token = data.token; // Ab Server ne khushi se User ka khas TOKEN dediya.
                localStorage.setItem('dc_token', token); // Abhi browser ki memory (local storage) ma save rakhlia 
                
                authForm.reset(); // Form fields khali ki
                checkAuth(); // Verification call k ab User dashboard me enter ho.
            } catch(e) { alert(e.message); }
        }
    });

    // --- CHECK KARNA KI KYA USER AUTHENTICATED HY? Verna Login Screen Dikhao ---
    async function checkAuth() {
        if (!token) {
            // LocalStorage mein Token nahi mila tou usy Login Screen pe bhejo Hide Class nikal ker overlay pe
            authOverlay.classList.remove('hidden'); 
            return;
        }
        try {
            // GET call bheji. Headers k andr apna token 'Bearer ...' sath bhijwaya! Backend taaley khol dga!
            const res = await fetch('/api/me', { headers: getHeaders() });
            if (!res.ok) throw new Error("Invalid token"); // Agur expiry hogya hy or DB se nai mila.
            
            const user = await res.json();
            userDisplay.textContent = user.name;  // Sidebar mein nechy kon Login h? uska naam dikha diya!
            authOverlay.classList.add('hidden'); // Overlay popup Login wala "Chupa" do!.
            
            loadSessions(); // Login ho gaya to jaldi se uske purany Chats la kar sidebar men sajaoo.
        } catch(e) {
            // Kharb token tha!
            localStorage.removeItem('dc_token'); // Browser me se kachhra token uda do
            token = null; 
            authOverlay.classList.remove('hidden'); // Phr se mard e Momin ko popup me lyy ao
        }
    }

    // --- LOGOUT BUTTON KI LOGIC ---
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('dc_token');  // memory saf
        token = null;
        chatContainer.innerHTML = ''; // Chat screen Safa chat karo
        chatContainer.appendChild(emptyState); // Vapis emptyState rakhdo (Welcome msg)
        emptyState.classList.remove('hidden'); 
        authOverlay.classList.remove('hidden'); // Vapsi phek diya Sign in screen!!
    });

    // --- CHAT SESSIONS SIDEBAR LOAD KARNE KI LOGIC ---
    async function loadSessions() {
        try {
            const res = await fetch('/api/sessions', { headers: getHeaders() }); // Sessions List Mnagi
            const data = await res.json();
            historyList.innerHTML = '';  // Sidebar jldi sy purany data se Khali krdeta
            
            data.forEach(s => { // loop! Har ek session ki list k ly
                const dev = document.createElement('div'); // Ek Container / Line Sidebar mein Banani h hr ek Title kliy
                dev.className = 'history-item';
                
                // Agar list ka id wahee hy jo tum ne current session khola h, tou use CSS deke Highight 'Active' kro
                if(s.id === currentSessionId) dev.classList.add('active'); 
                
                const span = document.createElement('span');
                span.textContent = s.title; // User ne jo pucha tha woh Title hy jesy "What is ai..."
                dev.appendChild(span);

                // Ek 'X' Cross icon bnaey delete karny k lye
                const del = document.createElement('button');
                del.className = 'delete-btn';
                del.innerHTML = '&times;'; 
                del.onclick = async (e) => {
                    e.stopPropagation(); // Delete dabay toh Session load wala event chalo nhi hone do! (Rok lia)
                    // Server ko session delete marny kaa bolo DELETE api par id dke
                    await fetch(`/api/sessions/${s.id}`, { method: 'DELETE', headers: getHeaders()});
                    if(currentSessionId === s.id) { // abhi wala he delete mardia gya hai...
                        currentSessionId = null;
                        clearChat(); // tou screen bhi clear karo bhai
                    }
                    loadSessions(); // sidebar phr se re-draw / update marooo!
                };
                dev.appendChild(del);

                dev.onclick = () => loadSessionHistory(s.id); // Jab click maray title pe to history aajy!!!
                historyList.appendChild(dev); // Sb kch DOM sidebr per append/daal diya!
            });
        } catch(e) { console.error(e); }
    }

    // --- CHAT HISTORY SCREEN PER PRINT KRNA ---
    async function loadSessionHistory(id) {
        currentSessionId = id; // Yaad rka k ab ye id k chat par hun mein!
        loadSessions(); // Ek br fer sidebar refresh hota key Highlight set ho jaey wahan pur!
        
        try {
            const res = await fetch(`/api/sessions/${id}`, { headers: getHeaders() });
            const history = await res.json(); // Array ayga msg, role ka
            
            clearChat(); 
            if(history.length > 0) emptyState.classList.add('hidden'); // Welcome msj Ghyab.
            
            // Jitny mesage they loop k zriye pury screen p "Chat Bubbles" ki tarah Lag gye!
            history.forEach(msg => {
                addChatBubble(msg.role, msg.content);
            });
            chatContainer.scrollTop = chatContainer.scrollHeight; // Aur screen ek dm sb say necht Scroll down hohgai.
        } catch(e) { console.error(e); }
    }

    // --- NAYA CHAT BUTTON DO ---
    newChatBtn.addEventListener('click', () => {
        currentSessionId = null; // Session Bhol jao or New chat p ajo
        loadSessions();
        clearChat(); // chat history purani mita do 
        emptyState.classList.remove('hidden'); // Wala DocuCompiler ka h1 heading DKHaaaoo
    });

    // Helper: Chat area srf msgs sy saaf kry (empty text na urah day)
    function clearChat() {
        Array.from(chatContainer.children).forEach(c => {
            if(c !== emptyState) c.remove();
        });
    }

    // MAIN JS UI FUNCTION: Ek msg chat men dikhana
    function addChatBubble(role, content) {
        emptyState.classList.add('hidden'); // Khali nhi hy chat ab
        const d = document.createElement('div');
        // Role 2 hen siraf yaha pe! 'user', 'assistant' inki css style.css m alg alag h (rang brangy)
        d.className = `chat-bubble bubble-${role}`; 
        
        // Jo \n ayenge usay Replace marky HTML ki 'BREAK' (<br>) line do
        d.innerHTML = content.replace(/\n/g, '<br>');
        
        chatContainer.appendChild(d); // Screen container pr thook daala isy!
        chatContainer.scrollTop = chatContainer.scrollHeight; // Nchaey dekhaynga 
    }

    // --- FILE UPLOAD DOKHA / TWEAK KARNA ---
    fileInput.addEventListener('change', () => {
        // Jab user koi docx ya pdf attach kre tou wo '📎 Attach File' ka naam change krwa dein taky usko smjhe ae ye lgg gai he file!!
        if(fileInput.files.length > 0) {
            fileIndicator.textContent = '📎 ' + fileInput.files[0].name; // Pehli kghaz r file ka naam 
            fileIndicator.style.background = '#e9d8fd'; // Purple jesa nishan asay deke dikho highlight
            fileIndicator.style.color = '#553c9a';
        } else {
            // Agr unhe kch glti se file delete / cnalcel kardi hai upload window me
            fileIndicator.textContent = '📎 Attach File';
            fileIndicator.style.background = '#edf2f7'; // Phr sufaid nishan bna deo
            fileIndicator.style.color = '#718096';
        }
    });

    // TEXTAREA KO Lamba HONey K Lye! 
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px'; // Jese enter daba k agy jata, text area chora hoga Auto.
    });

    // Enter Key daba k Bhi send Hosky baten.. Shift+enter pe nahi hoga blke NewLine aengi!
    chatInput.addEventListener('keydown', (e) => {
        if(e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            compileForm.dispatchEvent(new Event('submit')); // Khudb khud form bhej diya gya by firing an event
        }
    });

    // --- MAIN ENGINE API SUBMIT ---
    compileForm.addEventListener('submit', async (e) => {
        e.preventDefault(); 
        
        const textValue = chatInput.value.trim(); // kch lakha hi ? 
        const hasFile = fileInput.files.length > 0; // koi file he mery pas?
        
        if (!textValue && !hasFile) return; // Doon he khali ha to time zaya mat kor. Niklo yah ase!
        
        let fd = new FormData(); // Body bnao Data bhejhney kliye server ko
        
        if(hasFile) {
            fd.append('file', fileInput.files[0]);
            if(textValue) fd.append('query', textValue); // File k hone pe , Text ko hum "Sawaal/Query' ka naam dengee Backend k leiy.
        } else {
            fd.append('text', textValue); // Werna Normal sa Text document hi Hoga Bhalay para ho lamba..!
        }
        
        // Setings kya h ? Value nikal dropdown se usme daalo 'Moderate , aGRESSIVE ETX"
        fd.append('strategy', document.getElementById('strategy').value);
        fd.append('mode', document.getElementById('mode').value);
        if(currentSessionId) fd.append('session_id', currentSessionId); // Current ID jor denge usko 
        
        // USER k UI pr dikhyenga.. Ye string formate bas Display kelye hen Frontend pr Bhejny k lie upper FD ma hi.
        let userDisplayStr = textValue;
        if(hasFile) userDisplayStr = `[File attached: ${fileInput.files[0].name}]\n${textValue}`;
        if(!textValue && hasFile) userDisplayStr = `[File attached: ${fileInput.files[0].name}]`;
        
        addChatBubble('user', userDisplayStr); // Dikhaya screen peh Apna ChatBubble!
        
        chatInput.value = ''; // Safaaii ki input feild prr
        chatInput.style.height = 'auto'; 
        if(hasFile) {
            fileInput.value = ''; // Files bi mita do attach ho chukhi hn na !
            fileInput.dispatchEvent(new Event('change')); // style vaps reset hojaey
        }

        // Wait... jab thk server se reply ae, ekran (Screen) per ek "Processing" Message dal do
        const placeholder = document.createElement('div');
        placeholder.className = 'chat-bubble bubble-assistant';
        placeholder.innerHTML = '<i>Processing...</i>';
        chatContainer.appendChild(placeholder);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            // === FAST API SE RABTAY KA MAIN POINT !!! ===
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: getHeaders(), // Verify k hum kaun hen , Token pass!!
                body: fd               // form ka file data 
            });
            const data = await response.json(); // Javb aa Gaya!  JSON me badla
            if(!response.ok) throw new Error(data.detail); // Agur fat gaya Tou exception aeynge

            placeholder.remove(); // Wow jwb gya he ab processing htao pechy kr ke .
            
            // AI ka javaab lamba he to Jhor diya Question k saaat !
            let answerText = data.summary;
            if(data.answer && data.answer !== "QA dependencies not installed.") {
                answerText += `\n\n**A:** ${data.answer}`;
            }
            
            // Ab peheli daffa Server ko gya he Text.. toh Nya Session generate kr k dia he usney 
            if(!currentSessionId) {
                currentSessionId = data.session_id; // id save kerle mene JS me! 
                loadSessions(); // New naam or title add karne ko sidebar dobarta Render Kro !
            }
            
            addChatBubble('assistant', answerText); // Screen Pehlo ab tumharey lie javab ai gya ai ka !
            
        } catch(err) {
            placeholder.remove(); // Agar API server Off hy? Yahan pe aygay Error screen per.
            addChatBubble('assistant', 'Error: ' + err.message);
        }
    });

    // Peli dfa Website Refresh / Load hoty sath.. Start me Dekho Token hayen? Warna popup se login page !
    checkAuth();
});
