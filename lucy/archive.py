from lucy.models.package import Package
from lucy.models.user import User
from lucy.models.job import Job

from lucy.changes import parse_changes_file, ChangesFileException
from lucy.utils import cd, fglob

import os


def reject(changes, config):
    print("Rejecting: {source}/{version}".format(
        source=changes['source'],
        version=changes['version']))

    for f in changes.get_files() + [changes.get_filename()]:
        print("   Removing: %s" % (f))
        os.unlink(f)


def accept(changes, config, pool):
    print("Accepting: {source}/{version}".format(
        source=changes['source'],
        version=changes['version']))

    name = changes.get_package_name()
    version = changes['version']
    key = changes.validate_signature()

    try:
        who = User.get_by_key(key)
    except KeyError:
        # no such user
        return reject(changes, config)

    obj = Package(source=name,
                  version=version,
                  owner=who['_id'])
    obj.save()
    path = add_to_pool(pool, obj, changes)
    obj['path'] = path
    obj.save()
    os.unlink(changes.get_filename())

    for job in config['job_classes']:
        print("  -> New job: %s" % (job))
        Job(type=job, package=obj['_id']).save()


def uuid_to_path(uuid, base=None):
    nodes = uuid.split("-")
    ids = os.path.join(*nodes)
    path = os.path.join(*list(nodes[-1])[:4])
    path = os.path.join(ids, path)
    return path


def add_to_pool(pool, package, changes):
    uid = package['_id']
    ret = uuid_to_path(uid, base=pool)

    path = os.path.join(pool, ret)

    os.makedirs(path)
    for entry in changes.get_files():
        bn = os.path.basename(entry)
        dest = os.path.join(path, bn)
        os.rename(entry, dest)

    return ret


def process(config):
    pool = config['pool']
    incoming = config['incoming']

    with cd(incoming):
        def _pc(x):
            obj = parse_changes_file(x, directory=incoming)
            try:
                obj.validate(check_signature=True)
            except ChangesFileException:
                reject(obj, config)
                return None
            return obj

        for x in filter(lambda x: x is not None, fglob("*changes", _pc)):
            accept(x, config, pool)
