# This is a special api for single-parent mode rchain which each validator
# proposes block in sequence.
# The api would return list of validator servers and one best validator which
# would be the best to deploy based on the propose history.
from aiohttp.web import Request
from aiohttp import web
import asyncio
from settings import ValidatorInfo
from config import setting
import aiohttp
import json
from more_itertools import locate, first_true, one, ncycles, nth
from dataclasses import dataclass


available_validators = [v.to_dict() for v in setting.validator_list]

@dataclass()
class LatestInfo():
    block_number: int
    sender: str
    validator: ValidatorInfo


async def get_latest_block(validator: ValidatorInfo):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://'+ validator.host + ':' + str(validator.http_port) + '/api/blocks/1') as resp:
            blocks = await resp.json()
            latest_block = blocks[0]
            return LatestInfo(latest_block['blockNumber'], latest_block['sender'], validator)


async def validator(request: Request):
    latest_block_number_tasks = []
    for validator in setting.validator_list:
        latest_block_number_tasks.append(get_latest_block(validator))
    latest_infos = await asyncio.gather(*latest_block_number_tasks)
    max_block_numbers = max([i.block_number for i in latest_infos])
    latest = first_true(latest_infos, lambda x: x.block_number == max_block_numbers)
    index = one(locate(setting.validator_list, lambda x:x.pub_key == latest.sender))

    # why +2 ?
    # actually index validator should be the latest proposed validator
    # but it is possible that at this moment, the next validator is already trying
    # to propose a new block. So choosing the +2 validator is more reliable
    best = nth(ncycles(latest_infos,2),index+2)
    result = {
        "bestValidator": {
            "host": best.validator.host,
            "grpcPort": best.validator.grpc_port,
            "httpPort": best.validator.http_port,
            "latestBlockNumber": max_block_numbers
        },
        'validators': available_validators
    }
    return web.Response(body=json.dumps(result), headers={"Content-Type": "application/json"})
