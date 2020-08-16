from aiohttp.web import Application
from transaction import transaction, transfer
from status import handle_status
from api import total_supply, total_circulation, balance
from validators import validator
def setup_routes(app: Application):
    app.router.add_get('/getTransaction/{blockHash}', transaction)
    app.router.add_get('/status', handle_status)

    app.router.add_get('/api/total-supply', total_supply)
    app.router.add_get('/api/total-circulation',total_circulation )
    app.router.add_get('/api/balance/{address}', balance)
    app.router.add_get('/api/transfer/{address}', transfer)
    app.router.add_get('/api/validators', validator)
    return app