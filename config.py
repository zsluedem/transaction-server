import argparse
from concurrent.futures import ThreadPoolExecutor
import yaml
from settings import Settings

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config file path", action="store", dest="config", )
args = parser.parse_args()

with open(args.config) as f:
    config_content = f.read()

setting = Settings.parse_from_yaml(yaml.load(config_content))

executor = ThreadPoolExecutor(setting.NUM_CORE)
