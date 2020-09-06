# This is a special api for single-parent mode rchain which each validator
# proposes block in sequence.
# The api would return list of validator servers and one best validator which
# would be the best to deploy based on the propose history.
import asyncio
import random
from dataclasses import dataclass
from typing import List, Dict

import aiohttp
import cachetools
from fastapi import APIRouter
from more_itertools import locate, first_true, one, ncycles, nth, split_before, last, first
from pydantic import BaseModel

from rserver.settings import ValidatorInfo
from .config import setting

router = APIRouter()

validator_TTCache = cachetools.TTLCache(10e5, setting.VALIDATORS_TTL)
lock = asyncio.Lock()

VALIDATOR_CACHE_KEY = 'v'
NO_LATEST_BLOCK = -1


@dataclass()
class LatestInfo():
    block_number: int
    sender: str
    timestamp: int
    validator: ValidatorInfo


class NextToPropose(BaseModel):
    host: str
    grpcPort: int
    httpPort: int
    latestBlockNumber: int


class Validator(BaseModel):
    host: str
    grpc_port: int
    http_port: int
    latestBlockNumber: int
    timestamp: int


class ValidatorsResponse(BaseModel):
    nextToPropose: NextToPropose
    validators: List[Validator]


async def get_latest_block(validator: ValidatorInfo):
    http_scheme = 'https://' if validator.isHTTPS else 'http://'
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(setting.VALIDATOR_REQUEST_TIMEOUT)) as session:
            async with session.get(
                    http_scheme + validator.host + ':' + str(validator.http_port) + '/api/blocks/1') as resp:
                blocks = await resp.json()
                latest_block = first(blocks)
                return LatestInfo(block_number=latest_block['blockNumber'], sender=latest_block['sender'],
                                  validator=validator, timestamp=latest_block['timestamp'])
    except asyncio.TimeoutError as e:
        print("get latest block from {} failed with tiemout {} -> {}".format(validator.host,
                                                                             setting.VALIDATOR_REQUEST_TIMEOUT, e))
        return LatestInfo(block_number=NO_LATEST_BLOCK, sender='', validator=validator, timestamp=NO_LATEST_BLOCK)


@router.get('/api/validators')
async def validator():
    cache_data = validator_TTCache.get(VALIDATOR_CACHE_KEY)
    if cache_data:
        resp: ValidatorsResponse = cache_data
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
                latest_infos_no_exception = list(filter(lambda x: x.block_number != NO_LATEST_BLOCK, latest_infos))
                latest_num_dict: Dict[str, LatestInfo] = {i.validator.host: i for i in latest_infos}
                # get latest blocks from all the validators failed then randomly return the `nextToPropose`
                if len(latest_infos_no_exception) == 0:
                    best = random.choice(setting.validator_list)
                    max_block_numbers = NO_LATEST_BLOCK
                else:
                    max_block_numbers = max([i.block_number for i in latest_infos_no_exception])
                    latest = first_true(latest_infos_no_exception, lambda x: x.block_number == max_block_numbers)
                    index = one(locate(setting.validator_list, lambda x: x.pub_key == latest.sender))

                    # why +2 ?
                    # actually index validator should be the latest proposed validator
                    # but it is possible that at this moment, the next validator is already trying
                    # to propose a new block. So choosing the +2 validator is more reliable
                    best = nth(ncycles(setting.validator_list, 2), index + 2)
                split_validators = list(split_before(setting.validator_list, lambda x: x.host == best.host))
                if len(split_validators) == 1:
                    sorted_validators = one(split_validators)
                else:
                    sorted_validators = last(split_validators) + first(split_validators)

                validators = list(map(lambda x: Validator(host=x.host, grpc_port=x.grpc_port, http_port=x.http_port,
                                                          latestBlockNumber=latest_num_dict.get(x.host).block_number,
                                                          timestamp=latest_num_dict.get(x.host).timestamp),
                                      sorted_validators))

                nextToPropose = NextToPropose(host=best.host, grpcPort=best.grpc_port, httpPort=best.http_port,
                                              latestBlockNumber=max_block_numbers)
                resp = ValidatorsResponse(nextToPropose=nextToPropose, validators=validators)
                validator_TTCache[VALIDATOR_CACHE_KEY] = resp
    return resp.dict()
