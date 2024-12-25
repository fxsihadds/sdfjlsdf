import configparser
import logging
from pyrogram import Client


# SETUP LOGGING
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("Multi.log"), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

# LOAD CONFIG
config = configparser.ConfigParser()
config.read('config.ini')


# USER CLIENT
user = Client(
    "user",
    session_string=config['pyrogram']['session_string'],
    no_updates=True,
    workers=100,
    max_concurrent_transmissions=10,
)