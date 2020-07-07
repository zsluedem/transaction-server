import logging
import sys
from weakref import WeakValueDictionary

from aiohttp import web
from config import LOG_PATH, HOST, PORT
from routes import setup_routes


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(LOG_PATH)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.INFO)

app = web.Application()
app = setup_routes(app)

web.run_app(app, host=HOST, port=PORT)
