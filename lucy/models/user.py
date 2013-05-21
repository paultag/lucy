from lucy.models import LucyObject


class User(LucyObject):
    _type = 'users'

    def __init__(self, _id, name, email, gpg, **kwargs):
        super(User, self).__init__(_id=_id,
                                   gpg=gpg,
                                   name=name,
                                   email=email,
                                   **kwargs)

    @classmethod
    def get_by_email(cls, email):
        return cls.single({"email": email})

    @classmethod
    def get_by_key(cls, key):
        return cls.single({"gpg": key})

    get_by_uid = LucyObject.load
