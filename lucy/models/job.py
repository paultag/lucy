from lucy.models import LucyObject
from lucy.models.machine import Machine


class Job(LucyObject):
    _type = 'jobs'

    def __init__(self, type, package, package_type, builder=None,
                 finished_at=None, assigned_at=None, **kwargs):

        from lucy.models.source import Source
        from lucy.models.binary import Binary

        if package_type not in ["source", "binary"]:
            raise ValueError("package_type needs to be binary or source")

        if package_type == "source":
            package = Source.load(package)['_id']

        if package_type == "binary":
            package = Binary.load(package)['_id']

        if builder:
            builder = Machine.load(builder)['_id']

        if type == 'build':
            if 'arch' not in kwargs:
                raise ValueError("Binary build but not target arch")

            if 'suite' not in kwargs:
                raise ValueError("Binary build but not target suite")

        super(Job, self).__init__(
            type=type,
            package=package,
            builder=builder,
            finished_at=finished_at,
            assigned_at=assigned_at,
            package_type=package_type,
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
