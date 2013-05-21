from lucy import __appname__, __version__
from setuptools import setup


long_description = ""

setup(
    name=__appname__,
    version=__version__,
    scripts=[],
    packages=[
        'lucy',
    ],
    author="Paul Tagliamonte",
    author_email="tag@pault.ag",
    long_description=long_description,
    description='Lucy!',
    license="Expat",
    url="http://deb.io/",
    platforms=['any'],
    entry_points = {
        'console_scripts': [
            'lucy-nuke = lucy.cli.nuke:main',
            'lucy-process-incoming = lucy.cli.incoming:main',
            'lucy-init = lucy.cli.init:main',
            'lucyd = lucy.server:main',
        ],
    }
)
