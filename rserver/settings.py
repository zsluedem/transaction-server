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
    HOST: str
    PORT: int
    VALIDATORS_TTL: int
    validator_list: Optional[List[ValidatorInfo]]
    original_setting_dict: Dict
    VALIDATOR_REQUEST_TIMEOUT: int

    @classmethod
    def parse_from_yaml(cls, settings):
        if settings.get('VALIDATOR_LIST'):
            validator_list = [
                ValidatorInfo(host=v['host'], grpc_port=v['grpc_port'], http_port=v['http_port'], pub_key=v['pub_key'],
                              isHTTPS=v['isHTTPS']) for v in settings['VALIDATOR_LIST']]
        else:
            validator_list = None
        return cls(
                   HOST=settings['HOST'],
                   PORT=settings['PORT'],
                   validator_list=validator_list, original_setting_dict=settings,
                   VALIDATOR_REQUEST_TIMEOUT=settings['VALIDATOR_REQUEST_TIMEOUT'],
                   VALIDATORS_TTL=settings['VALIDATORS_TTL'])
