import cachetools
from fastapi import APIRouter
from fastapi.requests import Request
from pydantic import BaseModel
from rchain.client import RClient, RClientException
from rchain.crypto import PrivateKey
from rchain.vault import VaultAPI

from .config import setting

router = APIRouter()
request_faucet_TTCache = cachetools.TTLCache(10e5, setting.TESTNET_FAUCET_TTL)


class FaucetResponse(BaseModel):
    deployID: str
    message: str


@router.get('/testnet/faucet/{address}', response_model=FaucetResponse)
def faucet(address: str, request: Request):
    request_before = request_faucet_TTCache.get(request.client.host)
    if request_before:
        return FaucetResponse(deployID='', message='Your request for testnet rev is too high. Try later.')
    else:
        try:
            with RClient(setting.TARGET_TESTNET_HOST, setting.TARGET_TESTNET_PORT) as client:
                vault = VaultAPI(client)
                private = PrivateKey.from_hex(setting.TESTNET_FAUCET_PRIVATE_KEY)
                deployId = vault.transfer(private.get_public_key().get_rev_address(), address,
                                          setting.TESTNET_FAUCET_AMOUNT, private)
                request_faucet_TTCache[request.client.host] = address
                return FaucetResponse(deployID=deployId,
                                      message="Transfer to your address is done. You will receive the rev in some time")
        except RClientException as e:
            return FaucetResponse(deployID='',
                                  message="There is something with server {}. "
                                          "Please contact the maintainer to solve it.".format(e))
