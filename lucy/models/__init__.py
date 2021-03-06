import datetime as dt
import lucy.core
import uuid


def _get_table(what):
    return getattr(lucy.core.db, what)


class LucyObject(dict):
    _type = None

    def __init__(self, **kwargs):
        self['_type'] = self._type
        for k, v in kwargs.items():
            self[k] = v

    def _gen_uuid(self):
        return str(uuid.uuid1())

    def save(self):
        if self._type is None:
            raise ValueError("You done goofed, sucka")

        uuid = self.get('_id')
        self['updated_at'] = dt.datetime.utcnow()
        if uuid is None:
            uuid = self['_id'] = self._gen_uuid()
            self['created_at'] = dt.datetime.utcnow()
        _get_table(self._type).save(self)
        return uuid

    def delete(self):
        table = _get_table(self._type)
        table.remove({"_id": self['_id']})
        return uuid

    @classmethod
    def load(cls, what):
        table = _get_table(cls._type)
        obj = table.find_one({"_id": what})
        if obj is None:
            raise KeyError("No such object: `%s' found." % (what))
        return cls.from_dict(obj)

    @classmethod
    def query(cls, what, sort=None, sort_order=1,
              limit=None, page_count=None, page=0):

        table = _get_table(cls._type)
        pointer = table.find(what)
        if sort:
            pointer = pointer.sort(sort, sort_order)

        if limit:
            pointer = pointer.limit(limit)

        if page and page_count:
            offset = int(page) * int(page_count)
            pointer = pointer.skip(offset)

        if page_count:
            pointer = pointer.limit(page_count)

        for x in pointer:
            yield cls(**x)

    @classmethod
    def from_dict(cls, what):
        klass = cls(**what)
        return klass

    @classmethod
    def single(cls, query):
        os = cls.query(query)
        try:
            return next(os)
        except StopIteration:
            raise KeyError("Error. No such thing")
