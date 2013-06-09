from lucy import User, Source, Machine, Binary, Job
from lucy.archive import move_to_pool

from lucy.changes import parse_changes_file, ChangesFileException
from lucy.core import get_config
from lucy.utils import cd, fglob
#from lucy.mail import send_mail

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

    dsc = os.path.basename(changes.get_dsc())

    group = None
    if 'X-Lucy-Group' in changes:
        group = changes['X-Lucy-Group']

    obj = Source(source=changes['source'],
                 version=changes['version'],
                 owner=who['_id'],
                 group=group,
                 dsc=dsc)
    obj.save()

    path = move_to_pool(config, obj['_id'], changes)
    os.unlink(changes.get_filename())

    obj['path'] = path
    obj.save()

    print("ACCEPT: {source}/{version} for {owner} as {_id}".format(**obj))
    #send_mail("ACCEPTED: {source}/{version} for {owner} as {_id}".format(
    #    **obj), who['email'], "ACCEPTED!")

    add_jobs(obj, 'source', config, 'source', changes)


def add_jobs(package, package_type, config, klass, changes):

    for type in config['job_classes'][klass]:
        if klass == 'source':
            suite = "unstable"
            arch = "all"
        else:
            suite = package['suite']
            arch = package['arch']

        j = Job(package=package['_id'],
                package_type=package_type,
                suite=suite,
                arch=arch,
                type=type)
        print("  -> Job: ", j.save(), type)

    if klass == 'source':
        # add builds
        suite = changes['Distribution']
        for arch in config['arches']:
            j = Job(arch=arch,
                    suite=suite,
                    type='build',
                    package=package['_id'],
                    package_type=package_type)
            print("  -> Bin: ", j.save(), arch, suite)


def accept_binary(config, changes):
    key = changes.validate_signature()

    arch = changes['Architecture']
    if " " in arch:
        arches = set(arch.split(" "))
        if "all" in arches:
            arches.remove("all")

        arches = list(arches)
        if len(arches) != 1:
            return reject(config, changes, 'too-many-arches')

        arch = changes._data['Architecture'] = arches[0]


    suite = changes['Distribution']
    binaries = changes.get_files()

    try:
        job = changes['x-lucy-job']
    except KeyError:
        return reject(config, changes, 'no-job')

    try:
        job = Job.load(job)
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
    add_jobs(binary, 'binary', config, 'binary', changes)

    path = move_to_pool(config, binary['source'], changes, root=arch)
    os.unlink(changes.get_filename())
    print("accept binary")


def reject(config, changes, reason):
    print("reject", reason)
    # email luser with reason template
    for fpath in changes.get_files() + [changes.get_changes_file()]:
        os.unlink(fpath)
