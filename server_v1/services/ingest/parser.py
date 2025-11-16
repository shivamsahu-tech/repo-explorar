from tree_sitter_language_pack import get_parser as get_lang_parser
from core.logging import get_logger
from fastapi import HTTPException

logger = get_logger(__name__)

parsers_cache = {}

def get_parser(language: str):
    if language not in parsers_cache:
        logger.info("Parser is unavailable in cache, build one....")
        try:
            parsers_cache[language] = get_lang_parser(language)
        except Exception as e:
            logger.error(f"Failed to build parser for language : {language}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build parser for language : {language}"
            )
    
    return parsers_cache[language]

