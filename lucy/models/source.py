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


    def get_owner(self):
        return User.load(self['owner'])

    def get_jobs(self):
        for x in Job.by_package(self['_id']):
            yield x

    def get_reports(self):
        from lucy.models.report import Report
        for x in Report.query({"package": self['_id']}):
            yield x

    def get_binaries(self):
        from lucy.models.binary import Binary
        for x in Binary.query({"source": self['_id']}):
            yield x
