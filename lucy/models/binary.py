from lucy.models import LucyObject


class Binary(LucyObject):
    _type = 'binaries'

    def __init__(self, job, arch, suite, binaries, builder, **kwargs):
        from lucy.models.job import Job
        job = Job.load(job)['_id']
        if job['package_type'] != 'source':
            raise ValueError("Package from Job isn't a source package")

        source = job['package']

        super(Binary, self).__init__(job=job,
                                     arch=arch,
                                     suite=suite,
                                     builder=builder,
                                     binaries=binaries,
                                     **kwargs)
