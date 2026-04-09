import streamlit as st
import pandas as pd
import json
import os
from pyvis.network import Network
from aithra_nexus import AithraNexus

# --- PAGE CONFIG ---
st.set_page_config(page_title="AITHRA_WEB_PORTAL // SECURE_ACCESS", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    h1, h2, h3 { color: #00ff9d !important; font-family: 'Consolas', monospace; }
    .stTextInput>div>div>input { background-color: #0d1117; color: #00ff9d; border: 1px solid #1f2937; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN SCREEN ---
if not st.session_state.authenticated:
    st.title("[ AITHRA_WEB_PORTAL ]")
    st.subheader("ENCRYPTED ACCESS GATEWAY")
    
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("---")
            user = st.text_input("IDENT_ID (Username)")
            key = st.text_input("MASTER_KEY (Password)", type="password")
            
            if st.button("INITIALIZE_SESSION"):
                try:
                    # Attempt connection
                    nexus = AithraNexus(user, key)
                    st.session_state.nexus = nexus
                    st.session_state.username = user
                    st.session_state.authenticated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"ACCESS_DENIED: Critical Authentication Failure. {e}")

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
    
    tab1, tab2, tab3 = st.tabs(["CONCEPT_GRAPH", "KNOWLEDGE_EDITOR", "SEARCH_VAULT"])
    
    with tab1:
        st.subheader("NEURAL_NETWORK_MAP")
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
                    st.success("DAEMON_SYNC_COMPLETE")
            except Exception:
                st.error("DECRYPTION_FAILED: The Master Key in this session cannot unlock this node. Was it encrypted with a different key?")
        else:
            st.warning("VAULT_IS_EMPTY")

    with tab3:
        st.subheader("FTS5_QUANTUM_SEARCH")
        q = st.text_input("> ENTER_QUERY...")
        if q:
            results = nexus.search_vault(q)
            for r in results:
                with st.expander(f"[{r['type'].upper()}] {r['title']}"):
                    st.code(r['content'])
                    st.write(f"ID: {r['id']}")
            
            st.markdown("---")
            st.subheader("CONCEPTUAL_SEMANTIC_MATCHES")
            semantic_matches = nexus.semantic_search(q, limit=3)
            for sid, stitle, sim in semantic_matches:
                st.write(f"💡 **Possbile Relation**: {stitle} (Match: {sim:.2f})")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**VAULT_STATUS**: LOCKED_SESSION")
    st.sidebar.markdown(f"**NODES**: {len(nodes)}")
    st.sidebar.markdown(f"**ENCRYPTION**: AES_256_FERNET")
