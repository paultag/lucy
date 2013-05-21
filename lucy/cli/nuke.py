from lucy.models.config import Config
from lucy.core import db

from clint.textui import puts
import shutil
import sys
import os


def main():
    try:
        conf = Config.load('default')
    except KeyError:
        puts("Error: Need to init the db")
        sys.exit(1)

    pool = conf['pool']

    shutil.rmtree(pool)
    os.makedirs(pool)

    for x in db.collection_names():
        if x.startswith('system'):
            continue
        db.drop_collection(x)


if __name__ == "__main__":
    main()
