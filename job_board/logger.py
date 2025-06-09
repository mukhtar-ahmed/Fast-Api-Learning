import logging
import sys

# instance of logging
logger = logging.getLogger()

# create formatter
fotmatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# assign value
logger.setLevel(logging.INFO)

# Stream handler
stream_handler = logging.StreamHandler(stream=sys.stdout)

# formater on stream handler
stream_handler.setFormatter(fotmatter)

logger.handlers = [stream_handler]

logger.info("Logging start here")