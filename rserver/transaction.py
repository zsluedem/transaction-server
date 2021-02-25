import json
import logging
from asyncio import Lock, get_event_loop
from concurrent.futures import ThreadPoolExecutor
from typing import List
from weakref import WeakValueDictionary

from rchain.client import RClient
from rchain.param import mainnet_param
from .models import deployWithTransactionToTransactionInfo
from .config import setting
from fastapi import APIRouter
from fastapi.responses import Response
from .database.lmdb_storage import LMDB
from .models import TransactionInfo

LockControll = WeakValueDictionary()

executor = ThreadPoolExecutor(setting.NUM_CORE)
router = APIRouter()

database = LMDB({"path": setting.DB_PATH, "mapSize": setting.MAX_MEM})

def to_json_content(transactions: List[List[TransactionInfo]])-> str:
    jsonL = []
    for transactionList in transactions:
        if transactionList:
            jsonL.append([t.dict() for t in transactionList])
    result = json.dumps(jsonL)
    return result


def fetch_transactions(block_hash: str):
    client = RClient(setting.TARGET_RNODE_HOST, setting.TARGET_RNODE_PORT,
                     (('grpc.keepalive_time_ms', 10000), ('grpc.max_receive_message_length', 1619430400),),
                     True)
    client.install_param(mainnet_param)
    logging.info("request {} getTransaction from server {}".format(block_hash, setting.TARGET_RNODE_HOST))
    transactions = client.get_transaction(block_hash)
    logging.info("receive {} getTransaction {} from server {}".format(block_hash, transactions, setting.TARGET_RNODE_HOST))
    client.close()
    return transactions


async def get_transactions(block_hash: str):
    loop = get_event_loop()
    return await loop.run_in_executor(executor, fetch_transactions, block_hash)

@router.get('/getTransaction/{blockHash}')
async def transaction(blockHash: str):
    logging.info("Receive request on blockhash {}".format(blockHash))
    lock = LockControll.get(blockHash)
    if lock is None:
        lock = Lock()
        LockControll[blockHash] = lock
    async with lock:
        transactions = database.get(blockHash)
        if transactions is None:
            logging.info("There no result in database for {}, fetch data from server".format(blockHash))
            result = await get_transactions(blockHash)
            logging.info("Done fetch {} result {} from server".format(blockHash, result))
            transactions = deployWithTransactionToTransactionInfo(result)
            database.put(blockHash, transactions)
            logging.info("put data {} into db".format(blockHash))
        else:
            logging.info("The data {} , {} is already in db".format(blockHash, transactions[:20]))
        content = to_json_content(transactions)
    return Response(content=content, headers={"Content-Type": "application/json"})

@router.get('/api/transfer/{address}')
async def transfer(address: str):
    result = database.getAddressTransaction(address)
    return Response(content=json.dumps([t.dict() for t in result]), headers={"Content-Type": "application/json"})