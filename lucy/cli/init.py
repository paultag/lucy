from clint.textui import progress, puts
from clint import args

from lucy.models.machine import Machine
from lucy.models.config import Config
from lucy.models.user import User

import json


def main():
    if not args.files:
        raise Exception("WTF - need a config")

    config = args.files.pop(0)
    obj = json.load(open(config, 'r'))

    machines = obj['machines']
    configs = obj['configs']
    users = obj['users']

    puts("Loading users:")
    for conf in progress.bar(users):
        u = User(**conf)
        u.save()

    puts("Loading machines:")
    for conf in progress.bar(machines):
        m = Machine(**conf)
        m.save()

    puts("Loading configs:")
    for conf in progress.bar(configs):
        c = Config(**conf)
        c.save()


if __name__ == "__main__":
    main()
