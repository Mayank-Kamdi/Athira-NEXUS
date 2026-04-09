from aithra_nexus import AithraNexus
import os
import sqlite3

def run_full_demo():
    print("--- AITHRA-NEXUS SYSTEM INITIALIZATION ---")
    MASTER_PASS = "cyberpunk2026"
    TEST_DB = "test_vault.db"
    TEST_SALT = "test_salt.bin"
    
    # Cleanup previous tests
    if os.path.exists(TEST_DB): os.remove(TEST_DB)
    if os.path.exists(TEST_SALT): os.remove(TEST_SALT)

    # Patch AithraNexus to use test files
    # We'll just define a subclass to override the defaults for testing
    class TestNexus(AithraNexus):
        def __init__(self, password):
            from aithra_nexus import SecurityManager, DatabaseManager, OllamaManager, ResearchManager, AnalyticsExporter
            self.security = SecurityManager(password, salt_path=TEST_SALT)
            self.db = DatabaseManager(db_path=TEST_DB)
            self.ollama = OllamaManager()
            self.research = ResearchManager()
            self.exporter = AnalyticsExporter(self.db.db_path)

    # 1. Initialize Nexus
    nexus = TestNexus(MASTER_PASS)
    print(f"[SUCCESS] Vault '{TEST_DB}' Initialized and Locked with AES-256.")

    # 2. Add some nodes
    print("\n[+] Injecting intelligence nodes...")
    n1 = nexus.add_node("Startup Strategy", "Phase 1: Market Analysis on AI Agents. Phase 2: Local LLM deployment.")
    n2 = nexus.add_node("Threat Model 2026", "Primary threat: Data leakage via cloud LLMs. Mitigation: Use Aithra-Nexus local vault.")
    n3 = nexus.add_node("Quantum Prompt", "Act as a quantum physicist and explain superposition to a 5-year old.")
    
    # 3. Create Graph Links
    print("[+] Mapping connections in Knowledge Graph...")
    nexus.db.link_nodes(n1, n2, "mitigates_risk")
    nexus.db.link_nodes(n3, n1, "strategy_optimizer")

    # 4. Test Search (FTS5)
    print("\n[+] Triggering FTS5 Search for 'threat'...")
    results = nexus.search_vault("threat")
    for r in results:
        print(f"  FOUND: [{r['type'].upper()}] {r['title']}")
        print(f"  CONTENT (Decrypted): {r['content'][:100]}...")

    # 5. Test Graph Traversal
    print("\n[+] Analyzing Graph Neighbors for 'Startup Strategy'...")
    neighbors = nexus.get_neighbors(n1)
    for nb in neighbors:
        print(f"  LINKED: {nb['title']} ({nb['type']})")

    # 6. Test Exporter
    print("\n[+] Preparing metadata for Analytics Bridge...")
    msg = nexus.exporter.export_data()
    print(f"  EXPORTER_MSG: {msg}")

    print("\n--- DEMO COMPLETED SUCCESSFULLY ---")
    print("Files created: test_vault.db, test_salt.bin, analytics_cache.json")

    # Cleanup
    try:
        nexus.db.conn.close()
        os.remove(TEST_DB)
        os.remove(TEST_SALT)
    except: pass

if __name__ == "__main__":
    run_full_demo()
