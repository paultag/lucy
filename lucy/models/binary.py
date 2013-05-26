from lucy.models import LucyObject
from lucy.models.user import User
from lucy.models.source import Source


class Binary(LucyObject):
    _type = 'binaries'

    def __init__(self, source, arch, suite, binaries, builder, **kwargs):
        source = Source.load(source)['_id']

        super(Binary, self).__init__(source=source,
                                     arch=arch,
                                     suite=suite,
                                     builder=builder,
                                     binaries=binaries,
                                     **kwargs)
