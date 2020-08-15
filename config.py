import argparse
from concurrent.futures import ThreadPoolExecutor
from .settings import Settings

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config file path", action="store", dest="config", )
args = parser.parse_args()

with open(args.config) as f:
    config_content = f.read()

setting = Settings.parse_from_yaml(config_content)

executor = ThreadPoolExecutor(setting.num_core)
