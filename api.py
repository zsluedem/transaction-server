from aiohttp import web
from aiohttp.web import Request
import aiohttp
import json
import logging
from threading import RLock
import cachetools
from config import TARGET_RNODE_HOST, TARGET_RNODE_HTTP_PORT, USE_HTTPS, CACHE_TTL

# the total supply of the rchain mainnet is fixed
TOTAL_SUPPLY = 870663574.00
REV_TO_PHLO = 100000000

circulation_TTCache = cachetools.TTLCache(10e5, CACHE_TTL)
balance_TTCache = cachetools.TTLCache(10e5, CACHE_TTL)

http = "https://" if USE_HTTPS else 'http://'
target_host = "{}{}:{}".format(http, TARGET_RNODE_HOST, TARGET_RNODE_HTTP_PORT)
# coop addresses
coopSaleAddr = "11112GNiZeEQkMcSHRFgWbYvRuiKAN4Y44Jd1Ld6taFsGrw5JNHLtX"
coopTreasuryAddr = "111126JvMwXfDi6sBQNVwvSSNCMpXapTFTD1poQVzh7mzhN3WWn4kF"
coopResearchAddr = "1111zQqAW8zJxiAbPwtSi48WCHiQem5hBxkh3DLY7fe8V1Z947Uc4"
coopReserveAddr = "11112We8VJbQw7uvKUqvNc6L8X4EzC2yHHabRVZQC4J7M3vqf1b3yG"
coopDeploymentAddr = "11112DnHZWMxhRQH6AdfF1fh3VZbH5NW7wiq8xEsRy2DgczR5Yzsrd"
POSAddr = "1111V2DFLhSTYyDGwukVeYkoB3sHwEo78HviZsF8T8XxxRdLQ5j5P"

coopAddresses = [coopSaleAddr, coopTreasuryAddr, coopResearchAddr, coopReserveAddr, coopDeploymentAddr, POSAddr]

totalCirculationQuery = """
new return, rl(`rho:registry:lookup`), listOpsCh, RevVaultCh in{
  rl!(`rho:rchain:revVault`, *RevVaultCh) |
  rl!(`rho:lang:listOps`, *listOpsCh) |
  for (@(_, RevVault) <- RevVaultCh;
       @(_, ListOps) <- listOpsCh){
    new checkBalance, coopAddressesCh, balancesCh, sum, coopTotalCh in{
      contract checkBalance(addr, ret) = {
        new vaultCh, balanceCh in {
          @RevVault!("findOrCreate", *addr, *vaultCh) |
          for (@(true, vault) <- vaultCh){
            @vault!("balance", *balanceCh) |
            for (@balance <- balanceCh){
              ret!(balance)
            }
          }
        }
      } |
      contract sum(@a, @b, ret) = {
        ret!(a + b)
      }|
      coopAddressesCh!([
        "%s",
        "%s",
        "%s",
        "%s",
        "%s",
        "%s"
      ]) |
      for (@coopAddresses <- coopAddressesCh){
        @ListOps!("parMap", coopAddresses, *checkBalance, *balancesCh)|
        for(@balances <- balancesCh){
          @ListOps!("fold", balances, 0, *sum, *coopTotalCh)|
          for (@coopTotalBalance <- coopTotalCh){
            match (
              100000000000000000, // Original Mint
              12933642600000000  //  Burn
            ){
              (originMint, burned) => {
                return!(originMint - burned - coopTotalBalance)
              }
            }
          }
        }
      }
    }
  }
} 
""" %(coopSaleAddr, coopTreasuryAddr, coopResearchAddr, coopReserveAddr, coopDeploymentAddr, POSAddr)


def balanceQuery (address):
    query = """
new return, rl(`rho:registry:lookup`), RevVaultCh, vaultCh, balanceCh in {
  rl!(`rho:rchain:revVault`, *RevVaultCh) |
  for (@(_, RevVault) <- RevVaultCh) {
    @RevVault!("findOrCreate", "$addr", *vaultCh) |
    for (@(true, vault) <- vaultCh) {
      @vault!("balance", *balanceCh) |
      for (@balance <- balanceCh) {
        return!(balance)
      }
    }
  }
}"""
    return query.replace("$addr", address)

async def get_balance(address: str):
    query =  balanceQuery(address)
    ret = balance_TTCache.get(address)
    if ret:
        return ret
    else:
        async with aiohttp.ClientSession() as session:
            async  with session.post(target_host + '/api/explore-deploy', data=query) as resp:
                if resp.status != 200:
                    return -1
                else:
                    try:
                        content = await resp.text()
                        result = json.loads(content)
                        balance = result['expr'][0]['ExprInt']['data'] / REV_TO_PHLO
                        balance_TTCache[address] = balance
                        return balance
                    except Exception as e:
                        logging.error(e)
                        return -1


circulation_lock = RLock()
KEY_CIRCULATION = 'circulation'
async def get_total_circulation():
    ret = circulation_TTCache.get(KEY_CIRCULATION)
    if ret:
        return ret
    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(target_host + '/api/explore-deploy', data=totalCirculationQuery) as resp:
                if resp.status != 200:
                    return -1
                else:
                    try:
                        content = await resp.text()
                        result =  json.loads(content)
                        circulation =result['expr'][0]['ExprInt']['data'] / REV_TO_PHLO
                        circulation_TTCache[KEY_CIRCULATION] = circulation
                        return circulation
                    except Exception as e:
                        logging.error(e)
                        return -1

async def total_supply(request: Request):
    return web.Response(text=str(TOTAL_SUPPLY))

async def total_circulation(request: Request):
    result = await get_total_circulation()
    if result == -1:
        return web.Response(status=500)
    else:
        return web.Response(text=str(result))

async def balance(request: Request):
    address = request.match_info['address']
    result = await get_balance(address)
    if result == -1:
        return web.Response(status=500)
    else:
        return web.Response(text=str(result))
