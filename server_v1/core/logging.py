import logging
import sys 

def get_logger(name: str):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(levelname)s:     [%(name)s] %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger