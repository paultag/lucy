from lucy.models import LucyObject
from lucy.models.user import User


class Binary(LucyObject):
    _type = 'binaries'

    def __init__(self, source, arch, suite, binaries, builder, **kwargs):
        super(Binary, self).__init__(source=source,
                                     arch=arch,
                                     suite=suite,
                                     builder=builder,
                                     binaries=binaries,
                                     **kwargs)
