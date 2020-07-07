from aiohttp import web
from aiohttp.web import Request

async def handle_status(request: Request):
    return web.Response(body="OK")
