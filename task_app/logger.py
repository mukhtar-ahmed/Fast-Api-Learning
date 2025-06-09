import logging
import sys
from logtail import LogtailHandler

# instance of logging
logger = logging.getLogger("Task App")

# Asign
logger.setLevel(logging.INFO)

# create formatter
fotmatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Stream handler
stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(fotmatter)

# File handler
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(fotmatter)

# Better Stack
better_stack_handler = LogtailHandler(
    source_token="znZx8MXSvYU7FtAZF8YEdw2U",host="s1328639.eu-nbg-2.betterstackdata.com"
)

logger.handlers = [stream_handler, file_handler, better_stack_handler]

logger.info("starting logger is here")