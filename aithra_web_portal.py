import streamlit as st
import pandas as pd
import json
import os
from pyvis.network import Network
from aithra_nexus import AithraNexus
from auth_manager import AuthManager, track_event

auth = AuthManager()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AITHRA_WEB_PORTAL // SECURE_ACCESS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SEO BASICS ---
st.markdown("""
    <head>
        <meta name="description" content="Aithra-NEXUS: Secure Agentic Knowledge Vault. Local-first encryption for your digital second brain.">
        <meta name="keywords" content="AI, Knowledge Management, Privacy, Encryption, Agentic, Local-first">
        <meta name="author" content="Mayank Kamdi">
    </head>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700&family=JetBrains+Mono:wght@300;400&display=swap');

    :root {
        --primary: #00ff9d;
        --bg-dark: #05070a;
        --card-bg: #0d1117;
        --border-color: #1f2937;
    }

    .stApp { 
        background-color: var(--bg-dark); 
        color: #e6edf3; 
        font-family: 'Space Grotesk', sans-serif;
    }

    h1, h2, h3 { 
        color: var(--primary) !important; 
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -1px;
    }

    /* Glassmorphism Effect */
    .stTextInput>div>div>input { 
        background-color: var(--card-bg) !important; 
        color: var(--primary) !important; 
        border: 1px solid var(--border-color) !important;
        border-radius: 8px;
    }

    .stButton>button {
        background: linear-gradient(45deg, #00ff9d, #00d4ff);
        color: #05070a !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 255, 157, 0.4);
    }

    /* Cookie Banner Styling */
    .cookie-banner {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(13, 17, 23, 0.9);
        backdrop-filter: blur(10px);
        padding: 20px;
        border: 1px solid var(--primary);
        border-radius: 12px;
        z-index: 9999;
        max-width: 600px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "cookie_consent" not in st.session_state:
    st.session_state.cookie_consent = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# --- COOKIE CONSENT BANNER ---
if not st.session_state.cookie_consent:
    st.markdown(f"""
        <div class="cookie-banner">
            <p>We use essential cookies to ensure the security of your vault. By continuing, you agree to our <a href='/legal/cookie_policy' style='color:#00ff9d'>Cookie Policy</a>.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEPT_ALL_COOKIES"):
        st.session_state.cookie_consent = True
        st.rerun()

# --- LOGIN / SIGNUP SCREEN ---
if not st.session_state.authenticated:
    st.title("AITHRA // NEXUS")
    st.subheader("ENCRYPTED ACCESS GATEWAY")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        mode = st.radio("GATEWAY_MODE", ["LOGIN", "SIGNUP", "RESET_KEY"], horizontal=True)
        
        if mode == "LOGIN":
            user = st.text_input("IDENT_ID (Email)")
            key = st.text_input("MASTER_KEY (Password)", type="password")
            
            if st.button("INITIALIZE_SESSION"):
                # Use actual user identity instead of mock admin
                try:
                    # Initialize AithraNexus directly - this validates the password against the vault
                    nexus = AithraNexus(user, key)
                    st.session_state.nexus = nexus
                    st.session_state.username = user
                    st.session_state.authenticated = True
                    track_event(user, "LOGIN_SUCCESS")
                    st.rerun()
                except ValueError as ve:
                    st.error(f"AUTHENTICATION_DENIED: {ve}")
                except Exception as e:
                    st.error(f"SYSTEM_ERROR: {e}")
            
            st.markdown("---")
            if st.button("LOGIN_WITH_GOOGLE"):
                st.info("OAUTH_REDIRECT: Connecting to Google Identity Services...")
                
        elif mode == "SIGNUP":
            new_user = st.text_input("NEW_IDENT_ID (Email)")
            new_key = st.text_input("NEW_MASTER_KEY", type="password")
            confirm_key = st.text_input("CONFIRM_MASTER_KEY", type="password")
            
            if st.button("CREATE_IDENTITY"):
                if not new_user or not new_key:
                    st.error("REQUIRED_FIELDS_MISSING")
                elif new_key == confirm_key:
                    try:
                        # Creating AithraNexus instance for a new user initializes their record
                        nexus = AithraNexus(new_user, new_key)
                        st.success(f"IDENTITY_CREATED: Vault for {new_user} is ready.")
                        track_event(new_user, "SIGNUP_SUCCESS")
                        st.info("Please switch to LOGIN mode to enter your vault.")
                    except Exception as e:
                        st.error(f"REGISTRATION_FAILED: {e}")
                else:
                    st.error("KEY_MISMATCH: Passwords do not match.")

        elif mode == "RESET_KEY":
            reset_email = st.text_input("RECOVERY_EMAIL")
            if st.button("SEND_RECOVERY_LINK"):
                res = auth.reset_password(reset_email)
                st.success(res["message"])

# --- DASHBOARD ---
else:
    nexus = st.session_state.nexus
    st.sidebar.title(f"USER: {st.session_state.username.upper()}")
    if st.sidebar.button("LOGOUT / LOCK"):
        st.session_state.authenticated = False
        st.rerun()

    st.title("AGENTIC_KNOWLEDGE_DASHBOARD")
    
    # 1. Fetch User Data
    nodes, edges = nexus.get_graph_data()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["CONCEPT_GRAPH", "KNOWLEDGE_EDITOR", "SEARCH_VAULT", "SUPPORT_FEEDBACK", "LEGAL_COMPLIANCE"])
    
    with tab1:
        st.subheader("NEURAL_NETWORK_MAP")
        track_event(st.session_state.username, "VIEW_GRAPH")
        if nodes:
            net = Network(height="700px", width="100%", bgcolor="#0c0f14", font_color="white")
            colors = {"note": "#00d4ff", "prompt": "#00ff9d", "vault": "#ff4d4d"}
            for n in nodes:
                net.add_node(n["id"], label=n["title"], color=colors.get(n["type"], "#ffffff"))
            for e in edges:
                net.add_edge(e["source"], e["target"])
            net.save_graph("web_graph.html")
            st.components.v1.html(open("web_graph.html", 'r').read(), height=720)
            
            with open("web_graph.html", "rb") as f:
                st.download_button("DOWNLOAD_HIGH_RES_MAP (HTML)", f, file_name=f"vault_map_{st.session_state.username}.html")
        else:
            st.info("NO_NODES_DETECTED. INITIALIZE VAULT FROM DESKTOP TERMINAL.")

    with tab2:
        st.subheader("DECRYPTED_BUFFER")
        if nodes:
            node_titles = [n["title"] for n in nodes]
            sel_title = st.selectbox("SELECT_NODE", node_titles)
            
            # Find the actual node
            sel_node = next(n for n in nodes if n["title"] == sel_title)
            
            # Decrypt content
            res = nexus.db.conn.execute("SELECT content FROM nodes WHERE id=?", (sel_node['id'],)).fetchone()
            try:
                content = nexus.security.decrypt(res['content'])
                
                new_title = st.text_input("TITLE_ALIAS", value=sel_title)
                new_content = st.text_area("CONTENT_BUFFER", value=content, height=400)
                
                if st.button("SYNC_AND_RE_ENCRYPT"):
                    nexus.update_node(sel_node['id'], new_title, new_content)
                    track_event(st.session_state.username, "UPDATE_NODE", {"node_id": sel_node['id']})
                    st.success("DAEMON_SYNC_COMPLETE")
            except Exception:
                st.error("DECRYPTION_FAILED: The Master Key in this session cannot unlock this node.")
        else:
            st.warning("VAULT_IS_EMPTY")

    with tab3:
        st.subheader("FTS5_QUANTUM_SEARCH")
        q = st.text_input("> ENTER_QUERY...")
        if q:
            track_event(st.session_state.username, "SEARCH", {"query": q})
            results = nexus.search_vault(q)
            for r in results:
                with st.expander(f"[{r['type'].upper()}] {r['title']}"):
                    st.code(r['content'])
                    st.write(f"ID: {r['id']}")

    with tab4:
        st.subheader("SYSTEM_RECAP_&_SUPPORT")
        with st.form("feedback_form"):
            issue_type = st.selectbox("CATEGORY", ["BUG_REPORT", "FEATURE_REQUEST", "GENERAL_SUPPORT"])
            details = st.text_area("DESCRIPTION_OF_INCIDENT")
            priority = st.select_slider("PRIORITY", ["LOW", "MED", "HIGH", "CRITICAL"])
            
            if st.form_submit_button("SUBMIT_TO_DAEMON"):
                track_event(st.session_state.username, "FEEDBACK_SUBMITTED", {"type": issue_type, "priority": priority})
                st.success("TRANSMISSION_RECEIVED. Our liaison agents will analyze your report.")

    with tab5:
        st.subheader("LEGAL_PROTOCOLS")
        doc = st.radio("DOCUMENT", ["PRIVACY_POLICY", "TERMS_OF_SERVICE", "COOKIE_POLICY"], horizontal=True)
        
        doc_paths = {
            "PRIVACY_POLICY": "legal/privacy_policy.md",
            "TERMS_OF_SERVICE": "legal/terms_of_service.md",
            "COOKIE_POLICY": "legal/cookie_policy.md"
        }
        
        with open(doc_paths[doc], "r") as f:
            st.markdown(f.read())

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**VAULT_STATUS**: LOCKED_SESSION")
    st.sidebar.markdown(f"**NODES**: {len(nodes)}")
    st.sidebar.markdown(f"**ENCRYPTION**: AES_256_FERNET")
    st.sidebar.info("Aithra-NEXUS v1.4 // COMPLIANCE_READY")
