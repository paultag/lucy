from lucy import User, Source, Machine, Binary, Job
from lucy.archive import move_to_pool

from lucy.changes import parse_changes_file, ChangesFileException
from lucy.core import get_config
from lucy.utils import cd, fglob

import os



def process(config):
    incoming = config['incoming']
    pcf = lambda x: parse_changes_file(x, incoming)
    with cd(incoming):
        for changes in fglob("*changes", pcf):
            try:
                changes.validate()
            except ChangesFileException:
                reject(config, changes, "invalid")
                continue
            accept(config, changes)


def accept(config, changes):
    try:
        changes.validate_signature()
    except ChangesFileException:
        return reject(config, changes, "invalid-signature")

    if changes.is_source_only_upload():
        return accept_source(config, changes)

    if changes.is_binary_only_upload():
        return accept_binary(config, changes)

    return reject(config, changes, "not-only-sourceful")


def accept_source(config, changes):
    key = changes.validate_signature()

    try:
        who = User.get_by_key(key)
    except KeyError:
        return reject(changes, config, 'bad-user-account')

    obj = Source(source=changes['source'],
                 version=changes['version'],
                 owner=who['_id'])
    obj.save()

    path = move_to_pool(config, obj, changes)
    os.unlink(changes.get_filename())

    print("ACCEPT: {source}/{version} for {owner} as {_id}".format(**obj))
    add_jobs(obj, 'source', config['job_classes']['source'])


def add_jobs(package, package_type, types):
    for type in types:
        j = Job(package=package['_id'],
                package_type=package_type,
                type=type)
        print("  -> Job: ", j.save(), type)


def accept_binary(config, changes):
    key = changes.validate_signature()

    arch = changes['Architecture']
    suite = changes['Distribution']
    binaries = changes.get_files()

    try:
        job = changes['x-lucy-job']
    except KeyError:
        return reject(config, changes, 'no-job')

    try:
        job = Job.load(source)
    except KeyError:
        return reject(config, changes, 'invalid-job')

    try:
        buildd = Machine.get_by_key(key)
    except KeyError:
        return reject(config, changes, 'youre-not-a-machine')

    binary = Binary(job=job['_id'],
                    arch=arch,
                    suite=suite,
                    binaries=[os.path.basename(x) for x in binaries],
                    builder=buildd['_id'])
    binary.save()
    add_jobs(binary, 'binary', config['job_classes']['binary'])

    path = move_to_pool(config, source, changes, root=arch)
    os.unlink(changes.get_filename())
    print("accept binary")


def reject(config, changes, reason):
    print("reject", reason)
    # email luser with reason template
    for fpath in changes.get_files() + [changes.get_changes_file()]:
        os.unlink(fpath)
