from dataclasses import dataclass

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

    @classmethod
    def parse_from_yaml(cls, settings):
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
                   CACHE_TTL=settings['CACHE_TTL'])
