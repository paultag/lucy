from lucy.models import LucyObject
from lucy.models.machine import Machine
from lucy.models.package import Package


class Report(LucyObject):
    _type = 'reports'

    def __init__(self, report, builder, package, **kwargs):
        builder = Machine.load(builder)['_id']
        package = Package.load(package)['_id']
        super(Report, self).__init__(builder=builder,
                                     package=package,
                                     report=report,
                                     **kwargs)
