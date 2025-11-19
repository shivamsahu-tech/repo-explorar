from core.logging import get_logger
from services.llm.embedding import get_embeddings
from db.neo4j_client import get_neo4j_driver
from fastapi import HTTPException

logger = get_logger(__name__)
neo4j_driver = get_neo4j_driver()

CONTEXT_THRESHOLD = 50000


def retrieve_context(query: str, session_id: str, k: str = 10) -> str:
    try:
        logger.info(f"Embedding query: {query}")
        query_embedding = get_embeddings([query])[0]

        # staritn session
        with neo4j_driver.session() as session:
            # Fetching top 
            result = session.run(
                """
                CALL db.index.vector.queryNodes("code_embeddings", $k, $query_vector)
                YIELD node, score
                WHERE node.session_id = $session_id
                RETURN node, score
                ORDER BY score DESC
                """,
                query_vector=query_embedding,
                session_id=session_id,
                k=k
            )

            top_nodes = [record["node"] for record in result]
            logger.info(f"Top nodes found: {len(top_nodes)}")

            if not top_nodes:
                return f"Query: {query}\nNo relevant nodes found."

            top_ids = [node["id"] for node in top_nodes]

            # Fetch neighbours
            rel_result = session.run(
                """
                MATCH (n:CodeNode)
                WHERE n.session_id = $session_id AND n.id IN $top_ids

                MATCH (n)-[r]->(m:CodeNode)
                WHERE m.session_id = $session_id

                RETURN n AS source_node, m AS target_node, type(r) AS rel_type
                """,
                top_ids=top_ids,
                session_id=session_id
            )

            # Collect unique related nodes (avoid duplicates)
            related_nodes = []
            seen_ids = set()

            for record in rel_result:
                m = record["target_node"]
                if m["id"] not in seen_ids:
                    related_nodes.append(m)
                    seen_ids.add(m["id"])

            logger.info(f"Related outward neighbor nodes: {len(related_nodes)}")


        all_nodes = top_nodes + [n for n in related_nodes if n not in top_nodes]

        context_parts = ""
        current_length = len(context_parts)
        nodes_added = 0

        for node in all_nodes:
            block = f"""
                Name: {node['name']}
                Type: {node['ast_type']}
                File: {node['file']}
                Code: {node['code_str']}
                """
            block = "\n---------------------------------------------------------------------------\n" + block

            block_len = len(block)

            if current_length + block_len > CONTEXT_THRESHOLD:
                logger.info(
                    f"Threshold reached. Added {nodes_added} nodes out of {len(all_nodes)}"
                )
                break

            context_parts += block
            current_length += block_len
            nodes_added += 1


        logger.info(f"Final context length: {current_length} (nodes added: {nodes_added})")
        return context_parts

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to Fetch context from neo4j! | Error : {str(e)}"
        )
