# Introduction

Transaction database

# Requirement

    Python >=3.6

# Install

    git clone https://github.com/zsluedem/transaction-server.git
    cd transaction-server
    pip install -r requirements.txt
    
# Config

All the config should be in the environment variable

    DB_PATH=/path/to/db
    TARGET_RNODE_HOST=rchain.coop
    TARGET_RNODE_PORT=40401
    HOST=127.0.0.1
    PORT=7070
    NUM_CORE=2
    LOG_PATH=/path/to/log
    MAX_MEM=10  # megabytes for lmdb

# Docker

    docker run -d zsluedem/transaction-server

