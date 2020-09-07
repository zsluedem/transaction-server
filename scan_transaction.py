# pip install pyrchain
# pip install requests

from rchain.client import RClient
from rchain.param import testnet_param
from itertools import accumulate
import requests

step = 50
start = 1

transaction_host = 'http://localhost:7070'

node = 'observer.testnet.rchain.coop'
# node = 'node0.testnet.rchain-dev.tk'

with RClient(node, 40401,
     (('grpc.keepalive_time_ms', 10000),
      ('grpc.max_receive_message_length', 1619430400),)) as client:
    client.install_param(testnet_param)
    latest_block_number = client.show_blocks(1)[0].blockNumber

    def fetch_total_cost(s, e):
        blocks = client.get_blocks_by_heights(s, e-1)
        for b in blocks:
            requests.get('{}/getTransaction/{}'.format(
                transaction_host, b.blockHash))

    list(accumulate(range(start, latest_block_number, step), fetch_total_cost))
