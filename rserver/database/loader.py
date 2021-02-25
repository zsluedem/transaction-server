from typing import Dict
from .lmdb_storage import LMDB

AVAILABLE_DATABASE = {
    "lmdb": LMDB
}

class NoDatabaseImplementation(Exception):
    def __init__(self, database_type: str):
        self.database_type = database_type


def load_database(settings:Dict):
    database_cls= AVAILABLE_DATABASE.get(settings['type'])
    if database_cls:
        return database_cls(settings)
    else:
        raise NoDatabaseImplementation(settings['type'])