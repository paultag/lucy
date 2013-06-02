from lucy.models import LucyObject
from lucy.models.user import User
from lucy.models.job import Job
import lucy.core


class Source(LucyObject):
    _type = 'sources'

    def __init__(self, source, version, owner, dsc, **kwargs):
        owner = User.load(owner)['_id']
        super(Source, self).__init__(source=source,
                                     version=version,
                                     owner=owner,
                                     dsc=dsc,
                                     **kwargs)


    def get_owner(self):
        return User.load(self['owner'])

    def get_jobs(self):
        for x in Job.by_package(self['_id']):
            yield x

    def get_pending_jobs(self):
        for x in Job.query({
            "source": self['_id'],
            "finished_at": None
        }):
            yield x

    def get_reports(self):
        from lucy.models.report import Report
        for x in Report.query({"package": self['_id']}):
            yield x

    def get_binaries(self):
        from lucy.models.binary import Binary
        for x in Binary.query({"source": self['_id']}):
            yield x

    def get_job_status(self):
        db = lucy.core.db
        total = db.jobs.find({
            "source": self['_id']
        }).count()
        unfinished = db.jobs.find({
            "source": self['_id'],
            "finished_at": None
        }).count()
        return (total, unfinished)

    @classmethod
    def get_uploads_for_user(cls, who):
        for x in cls.query({"owner": who}):
            yield x
