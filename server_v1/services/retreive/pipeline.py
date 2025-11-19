from services.retreive.retrieve_context import retrieve_context
from services.llm.prompt_template import template
from services.llm.query_enhancement import enhance_query
from services.llm.llm import chat
from core.logging import get_logger

logger = get_logger(__name__)

def run_retreival_pipeline(session_id: str, query: str):
    print(session_id)
    # logger.info("Enhancing user query.......")
    # query = enhance_query(query)

    logger.info("Fetching Context..........")
    context = retrieve_context(query, session_id)

    prompt_template = template(query, context)

    logger.info("Getting LLM response...........")
    llm_response = chat(prompt_template)

    return llm_response
