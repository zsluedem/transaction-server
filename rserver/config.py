import argparse
import yaml
from .settings import Settings
from .database.loader import load_database

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config file path", action="store", dest="config", )
args = parser.parse_args()

with open(args.config) as f:
    config_content = f.read()

setting = Settings.parse_from_yaml(yaml.load(config_content))
