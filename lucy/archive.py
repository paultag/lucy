import shutil
import os


def uuid_to_path(uuid, base=None):
    nodes = uuid.split("-")
    ids = os.path.join(*nodes)
    path = os.path.join(*list(nodes[-1])[:4])
    path = os.path.join(ids, path)
    return path


def move_to_pool(config, package, changes, root=None):
    pool = config['pool']
    uid = package
    ret = uuid_to_path(uid, base=pool)
    path = os.path.join(pool, ret)
    if root:
        path = os.path.join(path, root)

    if os.path.exists(path):
        shutil.rmtree(path)  # odd. very odd.

    os.makedirs(path)
    for entry in changes.get_files():
        bn = os.path.basename(entry)
        dest = os.path.join(path, bn)
        os.rename(entry, dest)
    return ret
