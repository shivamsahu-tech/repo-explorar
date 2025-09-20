from typing import List, Dict
from utils.db_conntections import get_neo4j_driver, get_pinecone_connector
from utils.embedding import get_embeddings

neo4j_driver = get_neo4j_driver()
pc = get_pinecone_connector()
def search_code(query: str, index_name: str, max_results: int = 5) -> str:
    """Search code and return formatted results for RAG"""
    
    query_embedding = get_embeddings([query])[0]
    index = pc.Index(index_name)
    vector_results = index.query(
        vector=query_embedding, 
        top_k=max_results,
        include_metadata=True
    )
    
    if not vector_results['matches']:
        return "No matching code found."
    
    formatted_results = []
    
    with neo4j_driver.session() as session:
        for i, match in enumerate(vector_results['matches'], 1):
            node_id = match['id']
            
            result = session.run("""
                MATCH (n:CodeNode {id: $node_id})
                RETURN n.text as code, n.file as file, n.language as language, 
                       n.start_line as start_line, n.name as name, n.type as type
            """, node_id=node_id)
            
            record = result.single()
            if record:
                code = record['code']
                if isinstance(code, bytes):
                    code = code.decode('utf-8')
                
                formatted_results.append(f"""Result {i} (Score: {match['score']:.3f}):
Function: {record['name']}
Type: {record['type']}
File: {record['file']} (Line {record['start_line']})
Language: {record['language']}
Code: {code}
---""")
    
    return '\n'.join(formatted_results) if formatted_results else "No code details found."