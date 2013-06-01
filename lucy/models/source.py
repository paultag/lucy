from lucy.models import LucyObject
from lucy.models.user import User
from lucy.models.job import Job


class Source(LucyObject):
    _type = 'sources'

    def __init__(self, source, version, owner, **kwargs):
        owner = User.load(owner)['_id']
        super(Source, self).__init__(source=source,
                                     version=version,
                                     owner=owner,
                                     **kwargs)


    def get_pending_jobs(self):
        for x in Job.by_package(self['_id']):
            yield x
