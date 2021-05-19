import ipaddress

import cachetools
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
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


class FaucetRequest(BaseModel):
    address: str


@router.get('/testnet/faucet/', response_class=HTMLResponse)
def faucetPage():
    return """
<html>
  <head>
    <title>TestNet Faucet for RChain</title>
    <script src="https://unpkg.com/vue"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  </head>
  <body>
    <div id="app">
      <h1>TestNet Faucet for RChain</h1>
      <label>Input your testnet rev address :</label><br />
      <input v-model="address" /><br />
      <button v-on:click="submitFaucet()" />Submit</button>
      <h5>Result</h5>
      <label>DeployId: {{deployID}}</label><br />
      <label>Message: {{message}}</label><br />
    </div>

    <script>
      var app = new Vue({
        el: "#app",
        data: {
          address: "",
          deployId: "",
          message: ""
        },
        methods: {
          async submitFaucet() {
            const resp = await axios.post('/testnet/faucet', {"address": this.address})
            this.deployID = resp.data.deployID
            this.message = resp.data.message
          }
        }
      });
    </script>
  </body>
</html>
"""

# TODO remove it later
@router.get('/testnet/faucet/{old}')
def oldApi():
    return RedirectResponse('/testnet/faucet')

@router.post('/testnet/faucet/', response_model=FaucetResponse)
def faucetPost(faucetRequest: FaucetRequest, request: Request):
    address = faucetRequest.address
    realIp = request.headers.get('X-Real-IP')
    if realIp:
        addr = ipaddress.ip_address(realIp)
    else:
        addr = request.client.host
    request_before = request_faucet_TTCache.get(addr)
    if request_before:
        return FaucetResponse(deployID=request_before[1],
                              message='IP:{}, Your request for testnet rev to {} is too high. Try later'.format(
                                  addr, request_before[0]))
    else:
        try:
            with RClient(setting.TARGET_TESTNET_HOST, setting.TARGET_TESTNET_PORT) as client:
                vault = VaultAPI(client)
                private = PrivateKey.from_hex(setting.TESTNET_FAUCET_PRIVATE_KEY)
                deployId = vault.transfer_ensure(private.get_public_key().get_rev_address(), address,
                                                 setting.TESTNET_FAUCET_AMOUNT, private)
                request_faucet_TTCache[addr] = (address, deployId, request.client.host)
                return FaucetResponse(deployID=deployId,
                                      message="Transfer to your address is done. You will receive the rev in some time")
        except RClientException as e:
            return FaucetResponse(deployID='',
                                  message="There is something with server {}. "
                                          "Please contact the maintainer to solve it.".format(e))
