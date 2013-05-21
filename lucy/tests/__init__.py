from pymongo import Connection
import os

from lucy.models.config import Config
import lucy.core

ROOT = "%s/../../resources/" % (os.path.dirname(__file__))


def setup():
    connection = Connection('localhost', 27017)
    db = connection.lucy_test
    lucy.core.db = db
    for x in db.collection_names():
        if x.startswith('system'):
            continue

        db.drop_collection(x)

    name = "default"
    incoming = "%s/incoming/" % (ROOT)
    pool = "%s/pool/" % (ROOT)

    if name != Config(_id=name, incoming=incoming, pool=pool).save():
        raise Exception
