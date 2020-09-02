from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass()
class ValidatorInfo():
    host: str
    grpc_port: int
    http_port: int
    pub_key: str
    isHTTPS: bool

    def to_dict(self):
        return {'host': self.host, 'grpc_port': self.grpc_port, 'http_port': self.http_port}


@dataclass()
class Settings():
    DB_PATH: str
    TARGET_RNODE_HOST: str
    TARGET_RNODE_PORT: int
    TARGET_RNODE_HTTP_PORT: int
    USE_HTTPS: bool
    HOST: str
    PORT: int
    NUM_CORE: int
    LOG_PATH: str
    MAX_MEM: int
    CACHE_TTL: int
    VALIDATORS_TTL: int
    validator_list: Optional[List[ValidatorInfo]]
    original_setting_dict: Dict
    VALIDATOR_REQUEST_TIMEOUT: int

    TARGET_TESTNET_HOST: str
    TARGET_TESTNET_PORT: str
    TESTNET_FAUCET_TTL: int
    TESTNET_FAUCET_PRIVATE_KEY: str
    TESTNET_FAUCET_AMOUNT: int

    @classmethod
    def parse_from_yaml(cls, settings):
        if settings.get('VALIDATOR_LIST'):
            validator_list = [
                ValidatorInfo(host=v['host'], grpc_port=v['grpc_port'], http_port=v['http_port'], pub_key=v['pub_key'],
                              isHTTPS=v['isHTTPS']) for v in settings['VALIDATOR_LIST']]
        else:
            validator_list = None
        return cls(DB_PATH=settings['DB_PATH'],
                   TARGET_RNODE_HOST=settings['TARGET_RNODE_HOST'],
                   TARGET_RNODE_PORT=settings['TARGET_RNODE_PORT'],
                   TARGET_RNODE_HTTP_PORT=settings['TARGET_RNODE_HTTP_PORT'],
                   USE_HTTPS=settings['USE_HTTPS'],
                   HOST=settings['HOST'],
                   PORT=settings['PORT'],
                   NUM_CORE=settings['NUM_CORE'],
                   LOG_PATH=settings['LOG_PATH'],
                   MAX_MEM=settings['MAX_MEM'],
                   CACHE_TTL=settings['CACHE_TTL'],
                   validator_list=validator_list, original_setting_dict=settings,
                   VALIDATOR_REQUEST_TIMEOUT=settings['VALIDATOR_REQUEST_TIMEOUT'],
                   VALIDATORS_TTL=settings['VALIDATORS_TTL'],
                   TARGET_TESTNET_HOST=settings['TARGET_TESTNET_HOST'],
                   TARGET_TESTNET_PORT=settings['TARGET_TESTNET_PORT'],
                   TESTNET_FAUCET_TTL=settings['TESTNET_FAUCET_TTL'],
                   TESTNET_FAUCET_PRIVATE_KEY=settings['TESTNET_FAUCET_PRIVATE_KEY'],
                   TESTNET_FAUCET_AMOUNT=settings['TESTNET_FAUCET_AMOUNT'])
