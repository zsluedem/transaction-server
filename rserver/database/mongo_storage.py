import json

from pymongo import MongoClient
from typing import Dict, List, Optional
from .interface import DataBaseInterface
from ..models import TransactionInfo
from more_itertools import flatten

class MongoStorage(DataBaseInterface):
    def __init__(self, settings: Dict):
        super(MongoStorage, self).__init__(settings=settings)
        self.mongo_uri = settings.get("uri", "mongodb://localhost:27017")


    def _to_dict(self, transactions: List[List[TransactionInfo]]):
        result = []
        for transactionList in transactions:
            if transactionList:
                result.append([t.dict() for t in transactionList])
        return list(flatten(result))

    def put(self, blockHash: str, transactions: List[List[TransactionInfo]]):
        data = self._to_dict(transactions)


    def get(self, blockHash: str)->Optional[List[List[TransactionInfo]]]:
        with self._lmdb_env.begin(db=self._db) as txn:
            data = txn.get(blockHash.encode('utf8'))
            if data:
                jsonObj = json.loads(data.decode('utf8'))
                result = []
                for transactionList in jsonObj:
                    if transactionList:
                        result.append([TransactionInfo.parse_obj(t) for t in transactionList])
                return result
            else:
                return

    def getAddressTransaction(self, address: str)-> List[TransactionInfo]:
        result = []
        with self._lmdb_env.begin(db=self._db) as txn:
            cursor = txn.cursor()
            # block_transaction (hash, data)
            for block_transaction in iter(cursor):
                if block_transaction[1] != b'[]':
                    content = json.loads(block_transaction[1])
                    for deploy in content:
                        for transfer in deploy:
                            transferObj = TransactionInfo.parse_obj(transfer)
                            if transfer['toAddr'] == address:
                                result.append(transferObj)
                            elif transfer['fromAddr'] == address:
                                result.append(transferObj)
        result = sorted(result, key=lambda x: x.deploy.timestamp, reverse=True)
        return result