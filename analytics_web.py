import streamlit as st
import pandas as pd
import json
import os
import networkx as nx
from pyvis.network import Network
import seaborn as sns
import matplotlib.pyplot as plt

# Configuration
CACHE_FILE = "analytics_cache.json"

st.set_page_config(page_title="AITHRA-NEXUS // ANALYTICS", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0b0e14; color: #e6edf3; }
    .stApp { background-color: #0b0e14; }
    h1, h2, h3 { color: #00ff9d !important; font-family: 'Consolas', monospace; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not os.path.exists(CACHE_FILE):
        return None, None
    with open(CACHE_FILE, "r") as f:
        data = json.load(f)
    return data["nodes"], data["edges"]

st.title("AITHRA-NEXUS // INTELLIGENCE_REPORT")

nodes, edges = load_data()

if nodes is None:
    st.error("No analytics data found. Please run 'LAUNCH WEB REPORT' from the main Vault GUI.")
else:
    df_nodes = pd.DataFrame(nodes)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("CONCEPTUAL_GRAPH")
        # Build Pyvis Network
        net = Network(height="600px", width="100%", bgcolor="#161b22", font_color="white")
        
        # Color mapping
        colors = {"note": "#00d4ff", "prompt": "#00ff9d", "vault": "#ff4d4d", "research": "#ffcc00"}
        
        for n in nodes:
            net.add_node(n["id"], label=n["title"], title=f"Type: {n['type']}", color=colors.get(n["type"], "#ffffff"))
        
        for e in edges:
            net.add_edge(e["source"], e["target"], label=e["type"])
            
        net.toggle_physics(True)
        net.save_graph("temp_graph.html")
        st.components.v1.html(open("temp_graph.html", 'r').read(), height=620)

    with col2:
        st.subheader("KNOWLEDGE_DENSITY")
        type_counts = df_nodes["type"].value_counts()
        fig, ax = plt.subplots(facecolor='#0b0e14')
        ax.set_facecolor('#0b0e14')
        type_counts.plot(kind="pie", autopct='%1.1f%%', colors=[colors.get(t, "#fff") for t in type_counts.index], ax=ax, textprops={'color':"w"})
        st.pyplot(fig)

        st.subheader("ACTIVITY_PULSE")
        df_nodes["created_at"] = pd.to_datetime(df_nodes["created_at"])
        df_nodes["date"] = df_nodes["created_at"].dt.date
        activity = df_nodes.groupby("date").size()
        st.line_chart(activity)

st.sidebar.markdown("### SYSTEM_STATS")
if nodes:
    st.sidebar.metric("TOTAL_NODES", len(nodes))
    st.sidebar.metric("TOTAL_EDGES", len(edges))
    st.sidebar.info("Aithra-Nexus Agentic Vault v1.0")
