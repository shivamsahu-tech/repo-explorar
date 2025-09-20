from utils.storage import store_nodes_in_neo4j, store_nodes_in_pinecone
from utils.parsing import extract_all_nodes
from utils.git_clone import clone_repository, cleanup_repo
import json
from typing import List, Dict

def process_repository(repo_url: str) -> str:
    """Main function to process a repository"""
    session_id, repo_path = clone_repository(repo_url)
    
    try:
        print("entered")
        all_nodes = extract_all_nodes(repo_path)
        if not all_nodes:
            print("No nodes found")
            return session_id
        analyze_nodes_structure(all_nodes)
        index_name = f"repo-{session_id}"

        store_nodes_in_neo4j(all_nodes, session_id)
        store_nodes_in_pinecone(all_nodes, index_name)
        
        print(f"Processed {len(all_nodes)} nodes")
        return session_id
        
    finally:
        cleanup_repo(repo_path)

def analyze_nodes_structure(all_nodes: List[Dict]) -> None:
    """
    Analyze and print the structure of nodes to understand how data is stored
    """
    print("=" * 60)
    print("NODES STRUCTURE ANALYSIS")
    print("=" * 60)
    
    if not all_nodes:
        print("No nodes found!")
        return
    
    # Basic statistics
    print(f"📊 BASIC STATISTICS:")
    print(f"   Total nodes: {len(all_nodes)}")
    print(f"   Data type: {type(all_nodes)} containing {type(all_nodes[0]) if all_nodes else 'N/A'}")
    print()
    
    # Analyze structure of first few nodes
    print(f"🔍 STRUCTURE ANALYSIS:")
    
    # Get all unique keys across all nodes
    all_keys = set()
    for node in all_nodes:
        if isinstance(node, dict):
            all_keys.update(node.keys())
    
    print(f"   Unique keys found across all nodes: {sorted(all_keys)}")
    print(f"   Number of unique keys: {len(all_keys)}")
    print()
    
    # Analyze data types for each key
    print(f"📋 KEY-VALUE ANALYSIS:")
    key_types = {}
    key_examples = {}
    
    for key in sorted(all_keys):
        types_for_key = set()
        examples = []
        
        for node in all_nodes[:10]:  # Check first 10 nodes
            if isinstance(node, dict) and key in node:
                value = node[key]
                types_for_key.add(type(value).__name__)
                if len(examples) < 3:
                    examples.append(str(value)[:50] + ('...' if len(str(value)) > 50 else ''))
        
        key_types[key] = list(types_for_key)
        key_examples[key] = examples
        
        print(f"   '{key}':")
        print(f"      Type(s): {', '.join(types_for_key)}")
        print(f"      Examples: {examples}")
        print()
    
    # Show sample nodes
    print(f"📄 SAMPLE NODES:")
    sample_count = min(3, len(all_nodes))
    
    for i in range(sample_count):
        print(f"   Node {i + 1}:")
        node = all_nodes[i]
        if isinstance(node, dict):
            for key, value in node.items():
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"      {key}: {value_str}")
        else:
            print(f"      {node}")
        print()
    
    # Data consistency check
    print(f"🔧 CONSISTENCY CHECK:")
    if all_nodes:
        first_keys = set(all_nodes[0].keys()) if isinstance(all_nodes[0], dict) else set()
        consistent = True
        
        for i, node in enumerate(all_nodes[1:6]):  # Check first 5 nodes
            if isinstance(node, dict):
                node_keys = set(node.keys())
                if node_keys != first_keys:
                    print(f"   ⚠️  Node {i+2} has different keys than Node 1")
                    missing = first_keys - node_keys
                    extra = node_keys - first_keys
                    if missing:
                        print(f"      Missing: {missing}")
                    if extra:
                        print(f"      Extra: {extra}")
                    consistent = False
        
        if consistent:
            print(f"   ✅ All checked nodes have consistent key structure")
        print()
    
    # Memory usage estimate (rough)
    import sys
    total_size = sys.getsizeof(all_nodes)
    avg_node_size = total_size / len(all_nodes) if all_nodes else 0
    
    print(f"💾 MEMORY INFO:")
    print(f"   Estimated total size: ~{total_size} bytes ({total_size/1024:.1f} KB)")
    print(f"   Average size per node: ~{avg_node_size:.1f} bytes")
    
    print("=" * 60)


# Usage:
# all_nodes = extract_all_nodes("your_repo_path")
# analyze_nodes_structure(all_nodes)

