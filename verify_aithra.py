import sqlite3
from aithra_nexus import AithraNexus
import os

def verify():
    # Setup
    db_name = "aithra_nexus.db"
    salt_name = "salt.bin"
    if os.path.exists(db_name): os.remove(db_name)
    if os.path.exists(salt_name): os.remove(salt_name)
    
    password = "secret_master_key"
    nexus = AithraNexus(password)
    
    print("\n[1] Adding Nodes...")
    n1 = nexus.add_node("Project Alpha", "The classified details of project alpha.", "note")
    n2 = nexus.add_node("Alpha Prompt", "Summarize the project alpha notes.", "prompt")
    n3 = nexus.add_node("Database Schema", "Encrypted vault using SQLite and Fernet.", "note")
    
    print(f"Created nodes: {n1}, {n2}, {n3}")
    
    print("\n[2] Linking Nodes (Creating Knowledge Graph)...")
    nexus.link_nodes(n1, n2, "summarized_by")
    nexus.link_nodes(n1, n3, "design_doc")
    
    print("\n[3] Searching Vault (FTS5 + Decryption)...")
    results = nexus.search_vault("Alpha")
    for res in results:
        print(f"Found: {res['title']} -> {res['content']}")
    
    print("\n[4] Knowledge Graph Traversal...")
    links = nexus.get_graph(n1)
    print(f"Node 'Project Alpha' is connected to:")
    for link in links:
        print(f"  - [{link['relationship_type']}] -> {link['title']}")
        
    print("\n[5] Database Inspection (Verifying Encryption)...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM nodes LIMIT 1")
    blob = cursor.fetchone()[0]
    print(f"Encrypted Content in DB (first 50 chars): {blob[:50]}...")
    
    # Try searching directly for content in DB (should fail)
    cursor.execute("SELECT * FROM nodes WHERE content LIKE '%classified%'")
    if not cursor.fetchone():
        print("Success: Plain text content 'classified' not found in raw DB.")
    
    conn.close()

if __name__ == "__main__":
    verify()
