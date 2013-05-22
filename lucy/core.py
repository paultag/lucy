from pymongo import Connection


connection = Connection('localhost', 27017)
db = connection.lucy
config = None


def get_config():
    global config
    if config:
        return config

    from lucy.models.config import Config
    config = Config.load('default')
    return config
