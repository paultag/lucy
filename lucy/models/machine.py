from lucy.models import LucyObject
from lucy.models.user import User


class Machine(LucyObject):
    _type = 'machines'

    def __init__(self, _id, owner, auth, **kwargs):
        owner = User.load(owner)['_id']

        super(Machine, self).__init__(_id=_id,
                                      owner=owner,
                                      auth=auth,
                                      **kwargs)

    def auth(self, auth):
        return self['auth'] == auth
