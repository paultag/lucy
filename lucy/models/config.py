from lucy.models import LucyObject


class Config(LucyObject):
    _type = 'metadata'

    def __init__(self, _id, incoming, pool, **kwargs):
        super(Config, self).__init__(_id=_id,
                                     incoming=incoming,
                                     pool=pool,
                                     **kwargs)
