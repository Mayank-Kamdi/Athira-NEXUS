from aithra_nexus import AithraNexus

def init_demo():
    username = "Mayank"
    password = "123" # Simple password for demo
    
    print(f"Initializing Neural Hub for {username}...")
    nexus = AithraNexus(username, password)
    
    # Define Nodes
    nodes = [
        ("PROJECT_CHIMERA", "Central Intelligence Node for the 2026 Autonomous agent rollout. Aim: Zero-latency RAG."),
        ("NEURAL_FABRIC_v4", "The backbone of Chimera. Uses 4-bit quantized Mistral-7B-Instruct for core reasoning."),
        ("STEALTH_DAEMONS", "Background processes that scrape DuckDuckGo for real-time market shifts without detection."),
        ("CYBER_VOID_ENCRYPTION", "Custom AES-256-GCM implementation with rotating salts for the Chimera clusters."),
        ("PHASE_ONE_LAUNCH", "Scheduled for Q3 2026. Includes Desktop HUD and Web Analytics Portal."),
        ("GLOBAL_MARKET_TRENDS", "AI sector is shifting towards edge-computing and local-first privacy models.")
    ]
    
    # Create Nodes and store IDs
    node_ids = {}
    for title, content in nodes:
        nid = nexus.add_node(title, content)
        node_ids[title] = nid
        print(f"Captured: {title} [ID:{nid}]")
        
    # Link Nodes (Concept Graph)
    links = [
        ("PROJECT_CHIMERA", "NEURAL_FABRIC_v4"),
        ("PROJECT_CHIMERA", "PHASE_ONE_LAUNCH"),
        ("NEURAL_FABRIC_v4", "CYBER_VOID_ENCRYPTION"),
        ("STEALTH_DAEMONS", "PROJECT_CHIMERA"),
        ("STEALTH_DAEMONS", "GLOBAL_MARKET_TRENDS"),
        ("GLOBAL_MARKET_TRENDS", "PHASE_ONE_LAUNCH")
    ]
    
    for src, tgt in links:
        nexus.link_nodes(node_ids[src], node_ids[tgt])
        print(f"Linked: {src} <---> {tgt}")
        
    print("\nDEMO_DATA_INITIALIZED.")
    print(f"LOGIN: {username} // PASS: {password}")

if __name__ == "__main__":
    init_demo()
