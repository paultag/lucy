from lucy.models.machine import Machine
from lucy.models.source import Source
from lucy.models.binary import Binary
from lucy.models import LucyObject
from lucy.models.job import Job


class Report(LucyObject):
    _type = 'reports'

    def __init__(self, report, log, builder, package,
                 package_type, job, failed, **kwargs):

        if package_type not in ["source", "binary"]:
            raise ValueError("Bad package type")

        if package_type == 'source':
            package = Source.load(package)

        if package_type == 'binary':
            package = Binary.load(package)

        builder = Machine.load(builder)['_id']
        package = Package.load(package)['_id']
        job = Job.load(job)['_id']

        super(Report, self).__init__(package_type=package_type,
                                     builder=builder,
                                     package=package,
                                     report=report,
                                     failed=failed,
                                     log=log,
                                     job=job,
                                     **kwargs)
