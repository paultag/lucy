from pymongo import Connection


connection = Connection('localhost', 27017)
db = connection.lucy
config = None


def get_config(name='default'):
    global config
    if config:
        return config

    from lucy.models.config import Config
    config = Config.load(name)
    return config
