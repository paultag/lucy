from lucy import User, Source, Machine, Binary
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
    # source jobs



def accept_binary(config, changes):
    key = changes.validate_signature()

    arch = changes['Architecture']
    suite = changes['Distribution']
    binaries = changes.get_files()

    try:
        source = changes['x-lucy-source-package']
    except KeyError:
        return reject(config, changes, 'no-source-package')

    try:
        source = Source.load(source)
    except KeyError:
        return reject(config, changes, 'invalid-source-package')

    try:
        buildd = Machine.get_by_key(key)
    except KeyError:
        return reject(config, changes, 'youre-not-a-machine')

    binary = Binary(source=source['_id'],
                    arch=arch,
                    suite=suite,
                    binaries=[os.path.basename(x) for x in binaries],
                    builder=buildd['_id'])
    binary.save()
    # binary jobs

    path = move_to_pool(config, source, changes, root=arch)
    os.unlink(changes.get_filename())
    print("accept binary")


def reject(config, changes, reason):
    print("reject", reason)
    # email luser with reason template
    for fpath in changes.get_files() + [changes.get_changes_file()]:
        os.unlink(fpath)
