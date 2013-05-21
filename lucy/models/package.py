from lucy.models import LucyObject
from lucy.models.user import User


class Package(LucyObject):
    _type = 'packages'

    def __init__(self, source, version, owner, **kwargs):
        owner = User.load(owner)['_id']
        super(Package, self).__init__(source=source,
                                      version=version,
                                      owner=owner,
                                      **kwargs)

    @classmethod
    def get_all_versions(cls, source):
        for x in cls.query({"source": source}):
            yield cls.from_dict(x)
