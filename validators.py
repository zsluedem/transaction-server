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
from more_itertools import locate, first_true, one, ncycles, nth, split_before, last, first
from dataclasses import dataclass
import cachetools
import random


available_validators = [v.to_dict() for v in setting.validator_list]
validator_TTCache = cachetools.TTLCache(10e5, setting.VALIDATORS_TTL)
lock = asyncio.Lock()

VALIDATOR_CACHE_KEY = 'v'


@dataclass()
class LatestInfo():
    block_number: int
    sender: str
    validator: ValidatorInfo


async def get_latest_block(validator: ValidatorInfo):
    http_scheme = 'https://' if validator.isHTTPS else 'http://'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(setting.VALIDATOR_REQUEST_TIMEOUT)) as session:
        async with session.get(http_scheme+ validator.host + ':' + str(validator.http_port) + '/api/blocks/1') as resp:
            blocks = await resp.json()
            latest_block = blocks[0]
            return LatestInfo(latest_block['blockNumber'], latest_block['sender'], validator)


async def validator(request: Request):
    cache_data = validator_TTCache.get(VALIDATOR_CACHE_KEY)
    if cache_data:
        result = cache_data
    else:
        async with lock:
            cache_data = validator_TTCache.get(VALIDATOR_CACHE_KEY)
            if cache_data:
                return cache_data
            else:
                latest_block_number_tasks = []
                for validator in setting.validator_list:
                    latest_block_number_tasks.append(get_latest_block(validator))
                latest_infos = await asyncio.gather(*latest_block_number_tasks, return_exceptions=True)
                latest_infos_no_exception= list(filter(lambda x: not isinstance(x, Exception), latest_infos))

                # get latest blocks from all the validators failed then randomly return the `nextToPropose`
                if len(latest_infos_no_exception) ==0:
                    best = random.choice(setting.validator_list)
                    result = {
                        "nextToPropose": {
                            "host": best.host,
                            "grpcPort": best.grpc_port,
                            "httpPort": best.http_port,
                            "latestBlockNumber": 0
                        },
                        'validators': available_validators
                    }
                else:
                    max_block_numbers = max([i.block_number for i in latest_infos_no_exception])
                    latest = first_true(latest_infos_no_exception, lambda x: x.block_number == max_block_numbers)
                    index = one(locate(setting.validator_list, lambda x:x.pub_key == latest.sender))

                    # why +2 ?
                    # actually index validator should be the latest proposed validator
                    # but it is possible that at this moment, the next validator is already trying
                    # to propose a new block. So choosing the +2 validator is more reliable
                    best = nth(ncycles(setting.validator_list, 2), index + 2)
                    split_validators = list(split_before(available_validators, lambda x: x['host'] == best.host))
                    if len(split_validators) == 1:
                        sorted_validators = one(split_validators)
                    else:
                        sorted_validators = last(split_validators) + first(split_validators)
                    result = {
                        "nextToPropose": {
                            "host": best.host,
                            "grpcPort": best.grpc_port,
                            "httpPort": best.http_port,
                            "latestBlockNumber": max_block_numbers
                        },
                        'validators': sorted_validators
                    }
                    validator_TTCache[VALIDATOR_CACHE_KEY] = result
    return web.Response(body=json.dumps(result), headers={"Content-Type": "application/json"})
