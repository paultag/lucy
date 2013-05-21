from lucy.models.package import Package
from lucy.models.machine import Machine
from lucy.models import LucyObject


class Job(LucyObject):
    _type = 'jobs'

    def __init__(self, type, package, builder=None,
                 finished_at=None, **kwargs):

        package = Package.load(package)['_id']

        if builder:
            builder = Machine.load(builder)['_id']

        super(Job, self).__init__(
            type=type,
            package=package,
            builder=builder,
            finished_at=finished_at,
            **kwargs)

    def get_builder(self):
        builder = self.get('builder', None)
        if builder is None:
            return None
        return Machine.load(builder)

    def is_finished(self):
        return self.get('finished_at', None) is None

    @classmethod
    def unassigned_jobs(cls, **kwargs):
        k = kwargs.copy()
        k.update({"builder": None, "finished_at": None})

        for x in cls.query(**k):
            yield x

    @classmethod
    def unfinished_jobs(cls, **kwargs):
        k = kwargs.copy()
        k.update({"finished_at": None})

        for x in cls.query(**k):
            yield x
