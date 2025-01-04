import configparser
from configparser import ConfigParser

CONFIG_PATH = 'config.ini'

AUTH_SECTION = 'auth'

def load_config() -> ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def get_bot_token(loaded_config_parser: ConfigParser) -> str:
    return loaded_config_parser.get(AUTH_SECTION, 'bot_token')
