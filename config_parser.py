import configparser
from configparser import ConfigParser

CONFIG_PATH = 'config.ini'

AUTH_SECTION = 'auth'
ID_SECTION = 'id'

def load_config() -> ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def get_bot_token(loaded_config_parser: ConfigParser) -> str:
    return loaded_config_parser.get(AUTH_SECTION, 'bot_token')

def get_admin_ids(loaded_config_parser: ConfigParser) -> list[int]:
    return list(map(int, loaded_config_parser.get(ID_SECTION, 'admin_ids').split(',')))

def get_linkable_channel_ids(loaded_config_parser: ConfigParser) -> list[int]:
    return list(
        map(
            lambda channel_id:
                int("-100" + channel_id[1:]),
                loaded_config_parser.get(ID_SECTION, 'channel_ids').split(',')
        )
    )

