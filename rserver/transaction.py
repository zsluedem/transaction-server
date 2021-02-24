import base64
import json
import logging
import multiprocessing
import os
from asyncio import Lock, get_event_loop
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import List
from contextlib import contextmanager
from weakref import WeakValueDictionary

import lmdb
from aiohttp import web
from aiohttp.web import Request
from rchain.client import RClient
from rchain.param import mainnet_param
from rchain.report import DeployWithTransaction
from .config import setting
from fastapi import APIRouter
from fastapi.responses import Response

# LockControll = defaultdict(Lock)
LockControll = WeakValueDictionary()

executor = ThreadPoolExecutor(setting.NUM_CORE)
router = APIRouter()

# unused because of uncertainty
class LMDBWrapper:
    def __init__(self, path, map_size):
        self.path = path
        self.map_size = map_size
        self._db = lmdb.open(path, map_size=map_size)

    @contextmanager
    def begin(self, write=False):
        try:
            with self._db.begin(write=write) as txn:
                yield txn
        except (lmdb.MapResizedError, lmdb.MemoryError):
            self._db.close()
            self._db = lmdb.open(path=self.path, map_size=self.map_size)


lmdb_env = lmdb.open(setting.DB_PATH, map_size=setting.MAX_MEM, max_dbs=10)
lmdb_db = lmdb_env.open_db(b"transactions")


def to_dict(deploy_transactions: List[DeployWithTransaction]):
    result = []
    for deploy in deploy_transactions:
        deploy_info = {
            'deployer': deploy.deploy_info.deployer,
            'term': deploy.deploy_info.term,
            'timestamp': deploy.deploy_info.timestamp,
            'sig': deploy.deploy_info.sig,
            'sigAlgorithm': deploy.deploy_info.sigAlgorithm,
            'phloPrice': deploy.deploy_info.phloPrice,
            'phloLimit': deploy.deploy_info.phloLimit,
            'validAfterBlockNumber': deploy.deploy_info.validAfterBlockNumber,
            'cost': deploy.deploy_info.cost,
            'errored': deploy.deploy_info.errored,
            'systemDeployError': deploy.deploy_info.systemDeployError
        }
        one_deploy = [{
            'fromAddr': transaction.from_addr,
            'toAddr': transaction.to_addr,
            'amount': transaction.amount,
            'retUnforeable': base64.encodebytes(transaction.ret_unforgeable.SerializeToString()).decode('utf8'),
            'deploy': deploy_info,
            'success': transaction.success[0],
            'reason': transaction.success[1]
        } for transaction in deploy.transactions]

        result.append(one_deploy)
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
    return json.dumps(to_dict(transactions)).encode('utf8')


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
    block_hash_b: bytes = blockHash.encode('utf8')
    async with lock:
        with lmdb_env.begin(db=lmdb_db) as txn:
            result = txn.get(block_hash_b)
        if result is None:
            logging.info("There no result in database for {}, fetch data from server".format(blockHash))
            result = await get_transactions(blockHash)
            logging.info("Done fetch {} result {} from server".format(blockHash, result[:20]))
            with lmdb_env.begin(write=True, db=lmdb_db) as w_txn:
                w_txn.put(block_hash_b, result, db=lmdb_db)
            logging.info("put data {} into db".format(blockHash))
        else:
            logging.info("The data {} , {} is already in db".format(blockHash, result[:20]))
    return Response(content=result, headers={"Content-Type": "application/json"})

@router.get('/api/transfer/{address}')
async def transfer(address: str):
    result = []
    with lmdb_env.begin(db=lmdb_db) as txn:
        cursor = txn.cursor()
        # block_transaction (hash, data)
        for block_transaction in iter(cursor):
            if block_transaction[1] != b'[]':
                content = json.loads(block_transaction[1])
                for deploy in content:
                    for transfer in deploy:
                        if transfer['toAddr'] == address:
                            result.append(transfer)
                        elif transfer['fromAddr'] == address:
                            result.append(transfer)
    result = sorted(result, key=lambda x:x['deploy']['timestamp'], reverse=True)
    return Response(content=json.dumps(result), headers={"Content-Type": "application/json"})