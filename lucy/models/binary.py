from lucy.models import LucyObject


class Binary(LucyObject):
    _type = 'binaries'

    def __init__(self, job, arch, suite, binaries, builder, **kwargs):
        from lucy.models.job import Job
        job = Job.load(job)
        if job['package_type'] != 'source':
            raise ValueError("Package from Job isn't a source package")

        if 'source' not in kwargs:
            kwargs['source'] = job['package']

        super(Binary, self).__init__(job=job['_id'],
                                     arch=arch,
                                     suite=suite,
                                     builder=builder,
                                     binaries=binaries,
                                     **kwargs)

    def get_source(self):
        from lucy.models.source import Source
        return Source.load(self['source'])

    def get_reports(self):
        from lucy.models.report import Report
        for x in Report.query({"package": self['_id']}):
            yield x
