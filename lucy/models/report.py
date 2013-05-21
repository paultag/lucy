from lucy.models.machine import Machine
from lucy.models.package import Package
from lucy.models import LucyObject
from lucy.models.job import Job


class Report(LucyObject):
    _type = 'reports'

    def __init__(self, report, builder, package, job, **kwargs):
        builder = Machine.load(builder)['_id']
        package = Package.load(package)['_id']
        job = Job.load(job)['_id']
        super(Report, self).__init__(builder=builder,
                                     package=package,
                                     report=report,
                                     job=job,
                                     **kwargs)
