import lmdb
import argparse

parser = argparse.ArgumentParser(description='Scan transactions.')
parser.add_argument('--original', dest='original', type=str, help='original database')
parser.add_argument('--target', dest='target', type=str, help='target database', default='localhost')

args = parser.parse_args()

original = args.original
target = args.target
map_size = 500048576
original_lmdb_env = lmdb.open(original, map_size=map_size)

target_lmdb_env = lmdb.open(target, map_size=map_size, max_dbs=10)
db = target_lmdb_env.open_db("transaction".encode("utf8"))

with original_lmdb_env.begin() as  txn:
    c = txn.cursor()
    for i in c:
        key, value = i
        with target_lmdb_env.begin(write=True, db=db) as txn:
            txn.put(key, value, db=db)