import logging
import sys

# instance of logger
logger = logging.getLogger()
# asign level
logger.setLevel(logging.INFO)
# Formater
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Stream handler
stream_handler =  logging.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(formatter)

# asign handler
logger.handlers = [stream_handler]

logger.info("Logger start")