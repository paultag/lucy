import datetime as dt

from lucy.models.machine import Machine
from lucy.models import LucyObject


class Job(LucyObject):
    _type = 'jobs'

    def __init__(self, type, package, package_type, arch, suite,
                 builder=None, finished_at=None, assigned_at=None,
                 source=None, **kwargs):

        from lucy.models.source import Source
        from lucy.models.binary import Binary

        if package_type not in ["source", "binary"]:
            raise ValueError("package_type needs to be binary or source")

        if package_type == "source":
            package = Source.load(package)
            if source is None:
                source = package['_id']

        if package_type == "binary":
            package = Binary.load(package)
            if source is None:
                source = package['source']

        if package is None:
            raise ValueError("Bad package")

        package = package['_id']

        if builder:
            builder = Machine.load(builder)['_id']

        if source is None:
            raise ValueError("Bad source :(")

        super(Job, self).__init__(
            type=type,
            arch=arch,
            suite=suite,
            source=source,
            package=package,
            builder=builder,
            finished_at=finished_at,
            assigned_at=assigned_at,
            package_type=package_type,
            **kwargs)

    def get_package(self):
        from lucy.models.source import Source
        from lucy.models.binary import Binary

        if self['package_type'] == 'binary':
            return Binary.load(self['package'])

        if self['package_type'] == 'source':
            return Source.load(self['package'])

    def get_reports(self):
        from lucy.models.report import Report
        for x in Report.query({"job": self['_id']}):
            yield x

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
    def next_job(cls, suites, arches, types, **kwargs):
        k = kwargs.copy()
        k.update({"builder": None,
                  "finished_at": None,
                  "type": {"$in": types},
                  "suite": {"$in": suites},
                  "arch": {"$in": arches}})
        v = cls.single(k)
        return v

    @classmethod
    def dead_jobs(cls, howlong, **kwargs):
        cutoff = dt.datetime.utcnow() - howlong
        for x in cls.unfinished_jobs(**{
            "assigned_at": {"$lt": cutoff},
            "builder": {"$ne": None},
            "finished_at": None
        }):
            yield x

    @classmethod
    def by_package(cls, package, **kwargs):
        for x in cls.query({"package": package}):
            yield x

    @classmethod
    def unfinished_jobs(cls, **kwargs):
        k = {}
        k.update({"finished_at": None,
                  "builder": {"$ne": None}})
        k.update(kwargs.copy())

        return cls.query(k)

    @classmethod
    def assigned_jobs(cls, builder, **kwargs):
        return cls.unfinished_jobs(**{"builder": builder})
