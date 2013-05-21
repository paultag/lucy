import subprocess
import contextlib
import glob
import os


@contextlib.contextmanager
def cd(where):
    ncwd = os.getcwd()
    try:
        yield os.chdir(where)
    finally:
        os.chdir(ncwd)


def fglob(glo, globular):
    for x in glob.glob(glo):
        yield globular(x)


def run_command(command, stdin=None):
    if not isinstance(command, list):
        command = shlex.split(command)
    try:
        pipe = subprocess.Popen(command, shell=False,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError:
        return (None, None, -1)

    kwargs = {}
    if stdin:
        kwargs['input'] = stdin.read()

    (output, stderr) = pipe.communicate(**kwargs)
    return (output, stderr, pipe.returncode)
