from lucy.models.machine import Machine
from lucy.models.source import Source
from lucy.models.binary import Binary
from lucy.models import LucyObject
from lucy.models.job import Job


class Report(LucyObject):
    _type = 'reports'

    def __init__(self, report, builder, package,
                 package_type, job, failed, type=None, **kwargs):

        if package_type not in ["source", "binary"]:
            raise ValueError("Bad package type")

        loaded_package = None
        if package_type == 'source':
            try:
                loaded_package = Source.load(package)
            except KeyError:
                pass

        if package_type == 'binary':
            try:
                loaded_package = Binary.load(package)
            except KeyError:
                pass

        if loaded_package is None:
            raise KeyError("No such package")

        builder = Machine.load(builder)['_id']

        job = Job.load(job)

        if type is None:
            type = job['type']

        super(Report, self).__init__(package_type=package_type,
                                     builder=builder,
                                     package=loaded_package['_id'],
                                     report=report,
                                     job=job['_id'],
                                     type=type,
                                     failed=failed,
                                     **kwargs)
