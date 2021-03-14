import lmdb
import json

from typing import Dict, List, Optional
from .interface import DataBaseInterface
from ..models import TransactionInfo

class LMDB(DataBaseInterface):
    DATABASE = b"transactions"
    def __init__(self, settings: Dict):
        super(LMDB, self).__init__(settings=settings)
        self.path = settings.get("path", "transaction")
        self.map_size = settings.get("mapSize", 500048576)
        self._lmdb_env = lmdb.open(self.path, map_size=self.map_size, max_dbs=10)
        self._db = self._lmdb_env.open_db(self.DATABASE)


    def _to_dict(self, transactions: List[List[TransactionInfo]]):
        result = []
        for transactionList in transactions:
            if transactionList:
                result.append([t.dict() for t in transactionList])
        return result

    def put(self, blockHash: str, transactions: List[List[TransactionInfo]]):
        data = json.dumps(self._to_dict(transactions)).encode('utf8')
        with self._lmdb_env.begin(write=True, db=self._db) as w_txn:
            w_txn.put(blockHash.encode('utf8'), data, db=self._db)

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