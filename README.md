# ▲ AITHRA-NEXUS // AGENTIC_VAULT_OS

![Cyberpunk Dashboard](https://github.com/Mayank-Kamdi/Athira-NEXUS/raw/main/assets/banner.png) *(Placeholder for your future screenshot)*

> **"The future of knowledge is not storage; it's synthesis."**

Aithra-Nexus is a high-security, **Zero-Knowledge** Intelligence Management System designed for elite knowledge workers. It combines **local-first encryption (AES-256)** with an autonomous **Liaison AI** that discovers hidden conceptual links across your data while you work.

---

## ⚡ CORE CAPABILITIES

*   **🛡️ Zero-Knowledge Security**: All data is encrypted at rest using Fernet (AES-256). The Master Key is never persisted; it only lives in RAM.
*   **🤖 Autonomous Liaison Agent**: A background neural daemon (Mistral-7B via Ollama) that monitors your notes and proposes "Hidden Synapses" between related concepts.
*   **👁️ Multimodal Gaze**: Capture and ingest visual intelligence directly from your screen using the integrated Llava vision model.
*   **🕵️ Agentic Governance**: You remain the architect. AI-proposed links are held in a **PENDING** state until you manually approve or reject them.
*   **📈 GraphRAG Architecture**: Not just a database, but a neural fabric. Local FTS5 search combined with NetworkX graph projections.
*   **🕹️ Cyberpunk HUD**: A high-performance CustomTkinter GUI for localized work and a Streamlit-powered Web Portal for global graph visualization.

---

## 🛠️ TECH STACK

- **Core**: Python 3.10+
- **Database**: SQLite (FTS5 / Neural Graph)
- **Encryption**: `cryptography` (Advanced Fernet Implementation)
- **AI/LLM**: Ollama (Mistral-7B, Llava-Vision)
- **GUI**: CustomTkinter
- **Web/Analytics**: Streamlit, Plotly, Pyvis

---

## 🚀 INITIALIZATION PROTOCOL

### 1. Requirements
Ensure you have **Ollama** installed and the models pulled:
```bash
ollama pull mistral
ollama pull llava
```

### 2. Deployment
```bash
git clone https://github.com/Mayank-Kamdi/Athira-NEXUS.git
cd Athira-NEXUS
pip install -r requirements.txt
```

### 3. Execution
Launch the primary workstation:
```bash
python aithra_gui.py
```

---

## ⚖️ AGENTIC GUARDRAILS
Aithra-Nexus operates on the principle of **Human-in-the-Loop**. The AI acts as a **Liaison**, discovery insights that you might miss, but you hold the final authority to `APPROVE` or `REJECT` every conceptual link.

---

## 👤 DEVELOPER
**Mayank Kamdi**  
*Lead Architect of the Aithra Intelligence Ecosystem*

---
*Distributed under the MIT License. Data sovereignty guaranteed.*
