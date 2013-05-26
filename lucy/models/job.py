from lucy.models.source import Source
from lucy.models.binary import Binary
from lucy.models.machine import Machine
from lucy.models import LucyObject


class Job(LucyObject):
    _type = 'jobs'

    def __init__(self, type, package, package_type, builder=None,
                 finished_at=None, assigned_at=None, **kwargs):

        if package_type not in ["source", "binary"]:
            raise ValueError("package_type needs to be binary or source")

        if package_type == "source":
            package = Source.load(package)['_id']

        if package_type == "binary":
            package = Binary.load(package)['_id']

        if builder:
            builder = Machine.load(builder)['_id']

        super(Job, self).__init__(
            type=type,
            package=package,
            builder=builder,
            finished_at=finished_at,
            assigned_at=assigned_at,
            **kwargs)

    def get_builder(self):
        builder = self.get('builder', None)
        if builder is None:
            return None
        return Machine.load(builder)

    def is_finished(self):
        return not self.get('finished_at', None) is None

    @classmethod
    def unassigned_jobs(cls, **kwargs):
        k = kwargs.copy()
        k.update({"builder": None, "finished_at": None})

        for x in cls.query(k):
            yield x

    @classmethod
    def next_job(cls, **kwargs):
        k = kwargs.copy()
        k.update({"builder": None, "finished_at": None})
        v = cls.single(k)
        return v

    @classmethod
    def unfinished_jobs(cls, **kwargs):
        k = kwargs.copy()
        k.update({"finished_at": None})

        for x in cls.query(k):
            yield x

    @classmethod
    def assigned_jobs(cls, builder, **kwargs):
        return cls.unfinished_jobs(**{"builder": builder})
