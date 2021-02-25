from typing import List, Dict

from rchain.report import DeployWithTransaction
from ..models import TransactionInfo


class DataBaseInterface():
    def __init__(self, settings: Dict):
        pass

    def put(self, blockHash: str, transactions: List[DeployWithTransaction]):
        raise NotImplementedError()

    def get(self, blockHash: str)->List[List[TransactionInfo]]:
        raise NotImplementedError()

    def getAddressTransaction(self, address: str)-> List[TransactionInfo]:
        raise NotImplementedError()

