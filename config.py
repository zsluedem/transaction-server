import os
import multiprocessing
DB_PATH = os.environ.get("DB_PATH", "transactionsDB")
TARGET_RNODE_HOST = os.environ.get("TARGET_RNODE_HOST")
TARGET_RNODE_PORT = os.environ.get('TARGET_RNODE_PORT', 40401)
TARGET_RNODE_HTTP_PORT = os.environ.get("TARGET_RNODE_HTTP_PORT", 40403)
USE_HTTPS = os.environ.get("USE_HTTPS", 0)
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', 7070))
NUM_CORE = os.environ.get("NUM_CORE", multiprocessing.cpu_count() * 2)
LOG_PATH = os.environ.get("LOG_PATH", "/var/log/transactions.log")
MAX_MEM = int(os.environ.get("MAX_MEM", 10)) * 1048576  # Megabytes
CACHE_TTL = int(os.environ.get("CACHE_TTL", 60)) # second