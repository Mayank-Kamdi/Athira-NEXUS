import sqlite3
import pandas as pd
import json
import os

class AnalyticsExporter:
    """Extracts non-sensitive metadata for web reporting."""
    def __init__(self, db_path="aithra_nexus.db"):
        self.db_path = db_path

    def export_data(self):
        conn = sqlite3.connect(self.db_path)
        
        # 1. Export Nodes Metadata (No contents!)
        nodes_df = pd.read_sql_query("""
            SELECT n.id, n.type, f.title, n.version, n.created_at 
            FROM nodes n 
            JOIN fts_nodes f ON n.id = f.node_id
        """, conn)
        
        # 2. Export Edges
        edges_df = pd.read_sql_query("SELECT source_id, target_id, relationship_type FROM edges", conn)
        
        conn.close()
        
        # 3. Save to temp JSON for Streamlit to consume
        data = {
            "nodes": nodes_df.to_dict(orient="records"),
            "edges": edges_df.to_dict(orient="records")
        }
        
        with open("analytics_cache.json", "w") as f:
            json.dump(data, f)
        
        return "analytics_cache.json"

if __name__ == "__main__":
    exporter = AnalyticsExporter()
    exporter.export_data()
    print("Analytics data exported to analytics_cache.json")
