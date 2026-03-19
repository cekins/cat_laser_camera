import tomllib

CONF_FILE = 'settings.toml'


def load_conf() -> dict:
    with open(CONF_FILE, 'rb') as fp:
        return tomllib.load(fp)
