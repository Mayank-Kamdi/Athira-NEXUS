import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import os
from aithra_nexus import AithraNexus

# --- ULTIMATE CYBERPUNK PALETTE ---
COLOR_BG = "#020406"           # Purest Void Black
COLOR_SURFACE = "#0b0e14"      # Glassmorphism base
COLOR_ACCENT_GREEN = "#00ff9d" # Matrix Neon
COLOR_ACCENT_BLUE = "#00d4ff"  # Cyber Cyan
COLOR_ACCENT_RED = "#ff003c"   # Warning Red
COLOR_BORDER = "#1a1e26"       # Steel Grey
COLOR_TEXT_MAIN = "#e6edf3"    # Clean data white
COLOR_TEXT_GLOW = "#00ff9d"    # Text that glows

FONT_CONSOLAS_SM = ("Consolas", 11)
FONT_CONSOLAS_MD = ("Consolas", 14)
FONT_CONSOLAS_LG = ("Consolas", 24, "bold")
FONT_CONSOLAS_XL = ("Consolas", 48, "bold")
# Try to use a more elite font if possible
FONT_MONO = "Consolas" 

import winsound
def play_click():
    threading.Thread(target=lambda: winsound.Beep(800, 10), daemon=True).start()

class AithraGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AITHRA_NEXUS // AGENTIC_VAULT_OS")
        self.geometry("1500x950")
        self.configure(fg_color=COLOR_BG)
        
        self.nexus = None
        self.current_node_id = None
        
        # Start Login
        self.show_login()

    def show_login(self):
        self.login_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.login_frame.pack(expand=True, fill="both")
        
        # Futuristic Glow Logo
        ctk.CTkLabel(self.login_frame, text="▲", font=("Consolas", 80), text_color=COLOR_ACCENT_GREEN).pack(pady=(100, 0))
        ctk.CTkLabel(self.login_frame, text="AITHRA_NEXUS", font=FONT_CONSOLAS_XL, text_color=COLOR_ACCENT_GREEN).pack(pady=10)
        ctk.CTkLabel(self.login_frame, text="NEURAL_VAULT_DECRYPTION_PROTOCOL_v3.0", font=FONT_CONSOLAS_SM, text_color=COLOR_ACCENT_BLUE).pack()

        form = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        form.pack(pady=60)
        
        self.user_entry = self._cyber_entry(form, "USER_IDENTIFIER")
        self.user_entry.pack(pady=10)
        
        self.pass_entry = self._cyber_entry(form, "MASTER_ACCESS_KEY", is_pass=True)
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", lambda e: self.attempt_login())
        
        auth_btn = ctk.CTkButton(form, text="INITIALIZE_NEURAL_LINK", 
                                 command=self.attempt_login, 
                                 height=50, width=420,
                                 fg_color=COLOR_ACCENT_GREEN, text_color="black",
                                 hover_color=COLOR_ACCENT_BLUE, font=("Consolas", 18, "bold"),
                                 corner_radius=2)
        auth_btn.pack(pady=30)

    def _cyber_entry(self, master, placeholder, is_pass=False):
        return ctk.CTkEntry(master, placeholder_text=f"> {placeholder}", 
                            show="*" if is_pass else "",
                            width=420, height=45, 
                            fg_color="#05070a", border_color=COLOR_BORDER,
                            border_width=2, corner_radius=2,
                            font=FONT_CONSOLAS_MD, text_color=COLOR_ACCENT_BLUE)

    def attempt_login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        try:
            self.nexus = AithraNexus(user, password)
            self.login_frame.destroy()
            self.setup_main_ui()
        except Exception as e:
            messagebox.showerror("CRITICAL_FAILURE", f"AUTHENTICATION_REJECTED: {e}")

    def setup_main_ui(self):
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=3) # Editor
        self.grid_columnconfigure(2, weight=1) # HUD
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL: VAULT_EXPLORER ---
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="VAULT_OS // STORAGE", font=FONT_CONSOLAS_MD, text_color=COLOR_ACCENT_BLUE).pack(pady=(25, 5), padx=25, anchor="w")
        
        # High Tech Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_nodes())
        search_box = ctk.CTkEntry(self.sidebar, placeholder_text="SCAN_FILES...", 
                                  textvariable=self.search_var,
                                  fg_color=COLOR_BG, border_color=COLOR_BORDER,
                                  height=40, font=FONT_CONSOLAS_SM)
        search_box.pack(fill="x", padx=20, pady=15)
        
        self.node_list = tk.Listbox(self.sidebar, bg=COLOR_SURFACE, fg=COLOR_TEXT_MAIN, 
                                    borderwidth=0, highlightthickness=0, 
                                    font=("Consolas", 12), selectbackground=COLOR_ACCENT_BLUE, 
                                    selectforeground="black", activestyle="none")
        self.node_list.pack(fill="both", expand=True, padx=20, pady=5)
        self.node_list.bind("<<ListboxSelect>>", self.on_node_select)
        
        ctk.CTkButton(self.sidebar, text="+ CREATE_NEW_RECORD", command=self.add_new_node, 
                        fg_color="transparent", border_width=1, border_color=COLOR_ACCENT_GREEN,
                        text_color=COLOR_ACCENT_GREEN, font=FONT_CONSOLAS_SM, height=45).pack(fill="x", padx=20, pady=25)

        # --- PANEL: NEURAL_TERMINAL ---
        self.workstation = ctk.CTkFrame(self, fg_color="transparent")
        self.workstation.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        # Header Info
        header = ctk.CTkFrame(self.workstation, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Mode Tag
        self.mode_tag = ctk.CTkLabel(header, text=f"MODE: {self.nexus.current_intent}", 
                                      font=FONT_CONSOLAS_SM, text_color=COLOR_ACCENT_BLUE,
                                      fg_color=COLOR_SURFACE, padx=10)
        self.mode_tag.pack(side="top", anchor="w", pady=(0, 10))
        
        self.title_entry = ctk.CTkEntry(header, font=FONT_CONSOLAS_LG, 
                                        text_color=COLOR_ACCENT_GREEN, fg_color="transparent", 
                                        border_width=0, placeholder_text="NO_NODE_SELECTED")
        self.title_entry.pack(side="left", fill="x", expand=True)
        
        # Actions
        ctk.CTkButton(header, text="SYNC", width=100, fg_color=COLOR_ACCENT_GREEN, text_color="black", font=FONT_CONSOLAS_MD, command=self.save_node).pack(side="right", padx=5)
        ctk.CTkButton(header, text="PURGE", width=100, fg_color=COLOR_ACCENT_RED, text_color="white", font=FONT_CONSOLAS_MD, command=self.delete_node).pack(side="right", padx=5)

        # The Code/Note Buffer
        terminal_frame = ctk.CTkFrame(self.workstation, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
        terminal_frame.pack(fill="both", expand=True)
        
        # Visual styling for terminal
        ctk.CTkLabel(terminal_frame, text=" DECRYPTED_DATAFEED // v3.0 ", font=FONT_CONSOLAS_SM, text_color=COLOR_BORDER).pack(anchor="ne", padx=10, pady=5)
        
        self.text_editor = ctk.CTkTextbox(terminal_frame, font=("Consolas", 16), 
                                          fg_color="transparent", text_color=COLOR_TEXT_MAIN,
                                          wrap="word")
        self.text_editor.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # --- PANEL: INTELLIGENCE_HUD ---
        self.hud = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
        self.hud.grid(row=0, column=2, sticky="nsew")
        
        ctk.CTkLabel(self.hud, text="INTELLIGENCE HUD", font=FONT_CONSOLAS_MD, text_color=COLOR_ACCENT_BLUE).pack(pady=(25, 15), padx=25, anchor="w")
        
        # Control Cluster
        ctk.CTkButton(self.hud, text="LAUNCH_WEB_PORTAL", command=self.launch_portal, height=45,
                      fg_color="#10141b", border_width=1, border_color=COLOR_ACCENT_BLUE,
                      text_color=COLOR_ACCENT_BLUE, hover_color="#001a33").pack(fill="x", padx=25, pady=10)
        
        ctk.CTkButton(self.hud, text="AI_REFINEMENT", command=self.refine_node, height=45,
                        fg_color="#10141b", border_width=1, border_color=COLOR_ACCENT_GREEN,
                        text_color=COLOR_ACCENT_GREEN, hover_color="#001a11").pack(fill="x", padx=25, pady=10)

        ctk.CTkButton(self.hud, text="CAPTURE_SCREEN_GAZE", command=self.run_gaze, height=45,
                        fg_color="#10141b", border_width=1, border_color=COLOR_ACCENT_RED,
                        text_color=COLOR_ACCENT_RED, hover_color="#330000").pack(fill="x", padx=25, pady=10)

        # Agent Density Toggle
        self.temp_btn = ctk.CTkButton(self.hud, text="LIAISON: STRICT", command=self.toggle_temp, height=35,
                                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                                      text_color=COLOR_BORDER)
        self.temp_btn.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(self.hud, text="[ RELEVANT_NODES ]", font=FONT_CONSOLAS_SM, text_color=COLOR_BORDER).pack(pady=(20, 5))
        self.link_list = tk.Listbox(self.hud, bg=COLOR_SURFACE, fg=COLOR_ACCENT_BLUE, 
                                    borderwidth=0, highlightthickness=0, font=("Consolas", 11),
                                    selectbackground=COLOR_ACCENT_GREEN, selectforeground="black")
        self.link_list.pack(fill="both", expand=True, padx=25, pady=5)
        self.link_list.bind("<<ListboxSelect>>", self.jump_node)

        ctk.CTkLabel(self.hud, text="[ CONTEXT_SUGGESTIONS ]", font=FONT_CONSOLAS_SM, text_color=COLOR_ACCENT_GREEN).pack(pady=(20, 5))
        self.context_list = tk.Listbox(self.hud, height=4, bg=COLOR_BG, fg=COLOR_ACCENT_GREEN, font=FONT_CONSOLAS_SM, borderwidth=0)
        self.context_list.pack(fill="x", padx=25)
        self.context_list.bind("<<ListboxSelect>>", self.jump_context)

        # Agent Reasoning Log
        ctk.CTkLabel(self.hud, text=">> AGENT_GOVERNANCE", font=FONT_CONSOLAS_SM, text_color=COLOR_ACCENT_BLUE).pack(pady=(15, 5), padx=25, anchor="w")
        self.pending_list = tk.Listbox(self.hud, height=5, bg=COLOR_BG, fg=COLOR_TEXT_MAIN, font=FONT_CONSOLAS_SM)
        self.pending_list.pack(fill="x", padx=25)
        
        btn_row = ctk.CTkFrame(self.hud, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=5)
        ctk.CTkButton(btn_row, text="APPROVE", width=140, fg_color=COLOR_ACCENT_GREEN, text_color="black", command=self.approve_link).pack(side="left")
        ctk.CTkButton(btn_row, text="REJECT", width=140, fg_color=COLOR_ACCENT_RED, command=self.reject_link).pack(side="right")

        self.refresh_nodes()

    def launch_portal(self):
        # Use the verified venv path for reliability
        venv_st = os.path.join(".venv", "Scripts", "streamlit.exe")
        os.system(f'start cmd /k "{venv_st} run aithra_web_portal.py"')
        messagebox.showinfo("PORTAL", "Web Link Active at http://localhost:8501")

    def refresh_nodes(self):
        q = self.search_var.get()
        self.node_list.delete(0, tk.END)
        # Using the core search method for consistency
        if q:
            results = self.nexus.search_vault(q)
            self.nodes_data = [{"id": r['id'], "type": r['type'], "title": r['title']} for r in results]
        else:
            data = self.nexus.db.conn.execute("SELECT n.id, n.type, f.title FROM nodes n JOIN fts_nodes f ON n.id = f.node_id WHERE n.user_id=?", (self.nexus.user_id,)).fetchall()
            self.nodes_data = [dict(n) for n in data]
            
        for n in self.nodes_data: 
            self.node_list.insert(tk.END, f" ◈ {n['title'].upper()}")

    def on_node_select(self, e):
        sel = self.node_list.curselection()
        if sel: self.load_node(self.nodes_data[sel[0]]['id'])

    def load_node(self, node_id):
        play_click()
        self.current_node_id = node_id
        try:
            node = self.nexus.get_node(node_id)
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, node['title'])
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", node['content'])
            self.refresh_links(node_id)
            self.refresh_context(node['content'])
        except Exception as e:
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", f"--- [ DECRYPTION_LOCKED ] ---\n\n{str(e)}\n\nReason: The Master Key in this session cannot unlock this specific node segment. It may have been encrypted with a different Salt or a legacy password.")

    def refresh_context(self, content):
        """Finds semantic matches for the current buffer context."""
        def _run():
            matches = self.nexus.semantic_search(content[:300], limit=4)
            self.after(0, lambda: self._update_context_list(matches))
        threading.Thread(target=_run).start()

    def _update_context_list(self, matches):
        self.context_list.delete(0, tk.END)
        self.context_data = matches
        for m in matches:
            if m[0] != self.current_node_id:
                self.context_list.insert(tk.END, f" 💡 Suggestion: {m[1].upper()}")

    def jump_context(self, e):
        sel = self.context_list.curselection()
        if sel:
            self.load_node(self.context_data[sel[0]][0])

    def toggle_temp(self):
        if self.nexus.liaison.temperature == "low":
            self.nexus.liaison.temperature = "high"
            self.temp_btn.configure(text="LIAISON: CREATIVE", text_color=COLOR_ACCENT_GREEN, border_color=COLOR_ACCENT_GREEN)
        else:
            self.nexus.liaison.temperature = "low"
            self.temp_btn.configure(text="LIAISON: STRICT", text_color=COLOR_BORDER, border_color=COLOR_BORDER)

    def refresh_links(self, nid):
        self.link_list.delete(0, tk.END)
        neighbors = self.nexus.db.conn.execute("SELECT n.id, f.title, e.reasoning FROM edges e JOIN nodes n ON (e.source_id=n.id OR e.target_id=n.id) JOIN fts_nodes f ON n.id=f.node_id WHERE n.user_id=? AND (e.source_id=? OR e.target_id=?) AND n.id!=?", (self.nexus.user_id, nid, nid, nid)).fetchall()
        self.neigh_data = neighbors
        for l in neighbors: self.link_list.insert(tk.END, f" → {l['title'].upper()}")
        
    def jump_node(self, e):
        sel = self.link_list.curselection()
        if sel:
            target = self.neigh_data[sel[0]]
            self.load_node(target['id'])
            # Update reasoning box (repurposed for display)
            # self.reasoning_box.delete("1.0", tk.END)
            # self.reasoning_box.insert("1.0", f"LINK_LOG: {target['reasoning']}")

    def refresh_pending(self):
        self.pending_list.delete(0, tk.END)
        self.pending_data = self.nexus.db.conn.execute("SELECT e.id, f1.title as s, f2.title as t, e.reasoning FROM edges e JOIN fts_nodes f1 ON e.source_id=f1.node_id JOIN fts_nodes f2 ON e.target_id=f2.node_id WHERE e.status='PENDING' AND e.user_id=?", (self.nexus.user_id,)).fetchall()
        for p in self.pending_data:
            self.pending_list.insert(tk.END, f" {p['s']} <?> {p['t']}")

    def approve_link(self):
        sel = self.pending_list.curselection()
        if sel:
            self.nexus.db.conn.execute("UPDATE edges SET status='APPROVED' WHERE id=?", (self.pending_data[sel[0]]['id'],))
            self.nexus.db.conn.commit()
            self.refresh_pending(); self.refresh_links(self.current_node_id)

    def reject_link(self):
        sel = self.pending_list.curselection()
        if sel:
            self.nexus.db.conn.execute("DELETE FROM edges WHERE id=?", (self.pending_data[sel[0]]['id'],))
            self.nexus.db.conn.commit()
            self.refresh_pending()

    def run_gaze(self):
        threading.Thread(target=self._gaze_thread).start()
        messagebox.showinfo("GAZE", "Capturing Screen Visuals... Analyzing.")

    def _gaze_thread(self):
        nid = self.nexus.capture_gaze()
        if nid: self.after(0, lambda: (self.refresh_nodes(), self.load_node(nid)))

    def save_node(self):
        if self.current_node_id: 
            self.nexus.update_node(self.current_node_id, self.title_entry.get(), self.text_editor.get("1.0", tk.END))
            self.mode_tag.configure(text=f"MODE: {self.nexus.current_intent}")
            self.refresh_nodes()
            self.refresh_pending()

    def delete_node(self):
        if self.current_node_id and messagebox.askyesno("CONFIRM", "Permanently delete this neural segment?"):
            self.nexus.db.conn.execute("DELETE FROM nodes WHERE id=?", (self.current_node_id,))
            self.nexus.db.conn.execute("DELETE FROM fts_nodes WHERE node_id=?", (self.current_node_id,))
            self.nexus.db.conn.commit()
            self.current_node_id = None; self.title_entry.delete(0, tk.END); self.text_editor.delete("1.0", tk.END); self.refresh_nodes()

    def add_new_node(self):
        nid = self.nexus.add_node("NEW_SEGMENT", ">> DATA_CAPTURE_INIT...", "note")
        self.refresh_nodes(); self.load_node(nid)

    def refine_node(self):
        if self.current_node_id:
            threading.Thread(target=self._run_refine).start()
            messagebox.showinfo("AI", "Neural daemon refining prompt...")

    def _run_refine(self):
        self.nexus.generate_refined_prompt(self.current_node_id)
        self.after(0, self.refresh_nodes)

if __name__ == "__main__":
    AithraGUI().mainloop()
