# Introduction

Transaction database

# Requirement

    Python >=3.6

# Install

    git clone https://github.com/zsluedem/transaction-server.git
    cd transaction-server
    pip install -r requirements.txt
    
# Run

    python main.py -c /path/to/your/config.yml
    
# Config

Use yaml file to config. 

[Config Example](https://github.com/zsluedem/transaction-server/blob/master/config_example.yml)

# Docker

    docker run -v config.yml:/transaction_server/config.yml -d zsluedem/transaction-server

