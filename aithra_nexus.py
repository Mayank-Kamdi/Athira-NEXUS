import sqlite3
import os
import base64
import time
import json
import zipfile
import shutil
import threading
import webbrowser
import sys
from datetime import datetime
import requests
import networkx as nx

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class SecurityManager:
    """Security layer with multi-user salt management."""
    def __init__(self, master_password: str, username: str, db_conn: sqlite3.Connection):
        self.username = username
        self.db = db_conn
        self.salt = self._get_user_salt()
        self.key = self._derive_key(master_password)
        self.fernet = Fernet(self.key)

    def _get_user_salt(self):
        res = self.db.execute("SELECT salt FROM users WHERE username=?", (self.username,)).fetchone()
        if res: return res['salt']
        
        # New User Initialization
        salt = os.urandom(16)
        self.db.execute("INSERT INTO users (username, salt) VALUES (?, ?)", (self.username, salt))
        self.db.commit()
        return salt

    def _derive_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.salt, iterations=100000, backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def verify_password(self):
        # We store a "canary" node or just a small piece of encrypted data in the user table to check if our key is correct.
        res = self.db.execute("SELECT verification_token FROM users WHERE username=?", (self.username,)).fetchone()
        if res and res['verification_token']:
            try:
                self.decrypt(res['verification_token'])
                return True
            except:
                return False
        else:
            # First time setup for this user
            token = self.encrypt("AUTHENTICATED_SESSION_VALID")
            self.db.execute("UPDATE users SET verification_token=? WHERE username=?", (token, self.username))
            self.db.commit()
            return True

    def encrypt(self, data: str) -> bytes: return self.fernet.encrypt(data.encode())
    def decrypt(self, token: bytes) -> str: return self.fernet.decrypt(token).decode()

class DatabaseManager:
    def __init__(self, db_path: str = "aithra_nexus.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self):
        cursor = self.conn.cursor()
        # Multi-user Core Tables
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, salt BLOB, verification_token BLOB, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, content BLOB, type TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS node_versions (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER, content BLOB, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS edges (id INTEGER PRIMARY KEY AUTOINCREMENT, source_id INTEGER, target_id INTEGER, relationship_type TEXT, reasoning TEXT, status TEXT DEFAULT 'APPROVED', user_id INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS embeddings (node_id INTEGER PRIMARY KEY, vector BLOB)")
        
        # Schema Migrations (Add user_id if missing)
        self._migrate_schema()

        # Search Index (Updated to include user_id)
        try: cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_nodes USING fts5(title, node_id UNINDEXED, user_id UNINDEXED)")
        except: pass
        self.conn.commit()

    def _migrate_schema(self):
        """Adds multi-user columns to older database versions."""
        cursor = self.conn.cursor()
        
        # 1. Patch standard tables
        tables_to_patch = {
            "nodes": ["user_id INTEGER DEFAULT 1"],
            "edges": ["user_id INTEGER DEFAULT 1"]
        }
        for table, cols in tables_to_patch.items():
            existing_cols = [row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
            for col_def in cols:
                col_name = col_def.split()[0]
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
        
        # 1.5 Patch users table
        existing_user_cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
        if "verification_token" not in existing_user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN verification_token BLOB")
        
        # 1b. Patch edges for reasoning and status
        existing_edge_cols = [row[1] for row in cursor.execute("PRAGMA table_info(edges)").fetchall()]
        if "reasoning" not in existing_edge_cols:
            cursor.execute("ALTER TABLE edges ADD COLUMN reasoning TEXT")
        if "status" not in existing_edge_cols:
            cursor.execute("ALTER TABLE edges ADD COLUMN status TEXT DEFAULT 'APPROVED'")
        if "relationship_type" not in existing_edge_cols:
            cursor.execute("ALTER TABLE edges ADD COLUMN relationship_type TEXT")
        
        # 2. Rebuild FTS Table if user_id is missing
        fts_cols = [row[1] for row in cursor.execute("PRAGMA table_info(fts_nodes)").fetchall()]
        if fts_cols and "user_id" not in fts_cols:
            cursor.execute("DROP TABLE fts_nodes")
            cursor.execute("CREATE VIRTUAL TABLE fts_nodes USING fts5(title, node_id UNINDEXED, user_id UNINDEXED)")
            
        self.conn.commit()

    def get_user_id(self, username: str):
        return self.conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']

class AithraNexus:
    def __init__(self, username: str, password: str):
        self.db = DatabaseManager()
        self.username = username
        self.security = SecurityManager(password, username, self.db.conn)
        
        if not self.security.verify_password():
            raise ValueError("INVALID_MASTER_KEY: Decryption failed for this identity.")
            
        self.user_id = self.db.get_user_id(username)
        self.current_intent = "NEUTRAL"
        self.liaison = LiaisonAgent(self)
        self.liaison.start()

    def add_node(self, title, content, ntype="note"):
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO nodes (user_id, content, type) VALUES (?, ?, ?)", (self.user_id, self.security.encrypt(content), ntype))
        node_id = cursor.lastrowid
        self.db.conn.execute("INSERT INTO fts_nodes (title, node_id, user_id) VALUES (?, ?, ?)", (title, node_id, self.user_id))
        self.db.conn.commit()
        
        # Async Embedding Generation
        threading.Thread(target=self._generate_embedding, args=(node_id, content)).start()
        
        self.liaison.queue.put(node_id)
        self.refresh_intent()
        return node_id

    def _generate_embedding(self, node_id, content):
        """Generates semantic vector via Ollama."""
        try:
            res = requests.post("http://localhost:11434/api/embeddings", json={
                "model": "nomic-embed-text",
                "prompt": content
            }).json()
            vector = res['embedding']
            import numpy as np
            vec_blob = np.array(vector, dtype=np.float32).tobytes()
            self.db.conn.execute("INSERT OR REPLACE INTO embeddings (node_id, vector) VALUES (?, ?)", (node_id, vec_blob))
            self.db.conn.commit()
        except: pass

    def semantic_search(self, query, limit=5):
        """Finds conceptually similar nodes using cosine similarity."""
        try:
            res = requests.post("http://localhost:11434/api/embeddings", json={
                "model": "nomic-embed-text", 
                "prompt": query
            }).json()
            query_vec = res['embedding']
            
            import numpy as np
            nodes = self.db.conn.execute("SELECT e.node_id, e.vector, f.title FROM embeddings e JOIN fts_nodes f ON e.node_id=f.node_id WHERE f.user_id=?", (self.user_id,)).fetchall()
            
            scores = []
            for n in nodes:
                vec = np.frombuffer(n['vector'], dtype=np.float32)
                sim = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
                scores.append((n['node_id'], n['title'], sim))
            
            scores.sort(key=lambda x: x[2], reverse=True)
            return scores[:limit]
        except: return []

    def get_node(self, node_id):
        res = self.db.conn.execute("SELECT n.*, f.title FROM nodes n JOIN fts_nodes f ON n.id=f.node_id WHERE n.id=? AND n.user_id=?", (node_id, self.user_id)).fetchone()
        if not res: return None
        return {
            "id": res['id'],
            "title": res['title'],
            "type": res['type'],
            "content": self.security.decrypt(res['content']),
            "created_at": res['created_at']
        }

    def capture_gaze(self):
        """Captures screen and analyzes with vision model."""
        import pyautogui
        from PIL import Image
        import io
        
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        prompt = "Describe this screen capture in detail for a knowledge vault. Focus on text, code, or key visual elements."
        try:
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llava", 
                "prompt": prompt, 
                "images": [img_b64],
                "stream": False
            }).json()
            analysis = res.get('response', 'Visual data capture failed.')
            return self.add_node(f"SCREEN_GAZE_{datetime.now().strftime('%H%M%S')}", analysis, "vision")
        except: return None

    def update_node(self, node_id, title, content):
        # Archive current version
        old_node = self.db.conn.execute("SELECT content FROM nodes WHERE id=?", (node_id,)).fetchone()
        if old_node:
            self.db.conn.execute("INSERT INTO node_versions (node_id, content) VALUES (?, ?)", (node_id, old_node['content']))
        
        self.db.conn.execute("UPDATE nodes SET content = ? WHERE id = ? AND user_id = ?", (self.security.encrypt(content), node_id, self.user_id))
        self.db.conn.execute("UPDATE fts_nodes SET title = ? WHERE node_id = ? AND user_id = ?", (title, node_id, self.user_id))
        self.db.conn.commit()
        self.liaison.queue.put(node_id)
        self.refresh_intent()

    def generate_refined_prompt(self, node_id):
        """Uses AI to clean up and enhance a raw node's content."""
        node = self.get_node(node_id)
        if not node: return
        prompt = f"Refine the following knowledge node content to be more professional, concise, and insightful while maintaining all specific data. Content: {node['content']}"
        try:
            res = requests.post("http://localhost:11434/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False}).json()
            reflection = res.get('response', 'AI_REFINEMENT_FAILED')
            self.update_node(node_id, node['title'], reflection)
        except: pass

    def refresh_intent(self):
        """Infers the user's current 'Mode' from recent nodes."""
        recent = self.db.conn.execute("SELECT f.title FROM nodes n JOIN fts_nodes f ON n.id=f.node_id WHERE n.user_id=? ORDER BY n.created_at DESC LIMIT 5", (self.user_id,)).fetchall()
        titles = [r['title'] for r in recent]
        prompt = f"Given these note titles: {titles}. What is the primary INTENT mode? Respond with ONE WORD (e.g. STARTUP, CODING, FITNESS, PROJECT_ZERO)."
        try:
            res = requests.post("http://localhost:11434/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False}).json()
            self.current_intent = res.get('response', 'NEUTRAL').strip().upper()
        except: self.current_intent = "NEUTRAL"

    def search_vault(self, query):
        matches = self.db.conn.execute("SELECT node_id, title FROM fts_nodes WHERE user_id = ? AND title MATCH ?", (self.user_id, f"{query}*",)).fetchall()
        results = []
        for match in matches:
            node_data = self.db.conn.execute("SELECT * FROM nodes WHERE id=? AND user_id=?", (match['node_id'], self.user_id)).fetchone()
            if node_data:
                try: results.append({"id": match['node_id'], "title": match['title'], "type": node_data['type'], "content": self.security.decrypt(node_data['content'])})
                except: pass
        return results

    def get_graph_data(self):
        nodes = self.db.conn.execute("SELECT n.id, n.type, f.title, n.created_at FROM nodes n JOIN fts_nodes f ON n.id = f.node_id WHERE n.user_id=?", (self.user_id,)).fetchall()
        edges = self.db.conn.execute("SELECT source_id as source, target_id as target, relationship_type as type, reasoning FROM edges WHERE user_id=?", (self.user_id,)).fetchall()
        return [dict(n) for n in nodes], [dict(e) for e in edges]

    def link_nodes(self, id1, id2, rel="related", reasoning=None, status="APPROVED"):
        self.db.conn.execute("INSERT OR IGNORE INTO edges (source_id, target_id, user_id, relationship_type, reasoning, status) VALUES (?, ?, ?, ?, ?, ?)", 
                             (id1, id2, self.user_id, rel, reasoning, status))
        self.db.conn.commit()

import queue

class LiaisonAgent(threading.Thread):
    """Background intelligence that discovers conceptual links."""
    def __init__(self, nexus):
        super().__init__(daemon=True)
        self.nexus = nexus
        self.queue = queue.Queue()
        self.temperature = "low" # low, high
        
    def run(self):
        while True:
            node_id = self.queue.get()
            if node_id is None: break
            self.discover_hidden_links(node_id)
            self.queue.task_done()

    def discover_hidden_links(self, new_node_id):
        # 1. Fetch the new node content
        res = self.nexus.db.conn.execute("SELECT n.*, f.title FROM nodes n JOIN fts_nodes f ON n.id=f.node_id WHERE n.id=?", (new_node_id,)).fetchone()
        if not res: return
        
        new_title = res['title']
        try: new_content = self.nexus.security.decrypt(res['content'])
        except: return
        
        # 2. Fetch recent candidate nodes
        candidates = self.nexus.db.conn.execute("SELECT n.id, f.title, n.content FROM nodes n JOIN fts_nodes f ON n.id=f.node_id WHERE n.user_id=? AND n.id != ? ORDER BY n.created_at DESC LIMIT 10", (self.nexus.user_id, new_node_id)).fetchall()
        
        for cand in candidates:
            try:
                cand_content = self.nexus.security.decrypt(cand['content'])
                cand_title = cand['title']
                
                # Check for existing link
                exists = self.nexus.db.conn.execute("SELECT 1 FROM edges WHERE (source_id=? AND target_id=?) OR (source_id=? AND target_id=?)", (new_node_id, cand['id'], cand['id'], new_node_id)).fetchone()
                if exists: continue

                # LLM Comparison
                prompt = f"""Compare two concepts and decide if there is a logical relationship.
                Concept A: {new_title} - {new_content[:200]}
                Concept B: {cand_title} - {cand_content[:200]}
                
                Threshold: {self.temperature} (Low=Strict, High=Creative)
                If connected, respond ONLY with: YES | [Short 5-word Reason]
                If not, respond ONLY with: NO"""
                
                response = requests.post("http://localhost:11434/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False}).json()
                text = response.get('response', '').strip()
                
                if text.upper().startswith("YES"):
                    reason = text.split("|")[1].strip() if "|" in text else "Implicit logical bond."
                    self.nexus.link_nodes(new_node_id, cand['id'], rel="autonomous_link", reasoning=reason, status="PENDING")
                    print(f"[AGENT] Proposed Insight: {new_title} <--> {cand_title} | {reason}")
            except: continue
        
        # Clear secret content from RAM (implicitly handled by function scope exit, but good to be careful)
        del new_content
