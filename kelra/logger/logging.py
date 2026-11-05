import logging
import os

import config


class ConnectionHandler(logging.Handler):
    def emit(self, record):
        for X in ["OSErro", "TimeoutError", "socket"]:
            if X in record.getMessage():
                os.execl("/bin/bash", "bash", "start.sh")


logging.basicConfig(level=logging.INFO, format="%(name)s[%(levelname)s]: %(message)s")
logger = logging.getLogger(f"{config.BOT_NAME}")
connection_handler = ConnectionHandler()

for lib in {
    "pyrogram",
    "gunicorn",
    "flask",
    "pytgcalls",
    "aiorun",
    "asyncio",
    "hydrogram",
}:
    logging.getLogger(lib).setLevel(logging.ERROR)
    logging.getLogger(lib).addHandler(connection_handler)
