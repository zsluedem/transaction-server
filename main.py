import logging
import sys
from weakref import WeakValueDictionary

from aiohttp import web
from config import setting
from routes import setup_routes


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(setting.LOG_PATH)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
root = logging.getLogger()
root.addHandler(handler)
std_handler = logging.StreamHandler(sys.stdin)
std_handler.setFormatter(formatter)
std_handler.setLevel(logging.INFO)
root.addHandler(std_handler)
root.setLevel(logging.INFO)

app = web.Application()
app = setup_routes(app)

web.run_app(app, host=setting.HOST, port=setting.PORT)
