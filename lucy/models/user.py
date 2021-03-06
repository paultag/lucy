from lucy.models import LucyObject


class User(LucyObject):
    _type = 'users'

    def __init__(self, _id, auth, name, email, gpg, **kwargs):
        super(User, self).__init__(_id=_id,
                                   auth=auth,
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

    def get_uploads(self):
        from lucy import Source
        return Source.get_uploads_for_user(self['_id'])

    def auth(self, auth):
        return self['auth'] == auth

    get_by_uid = LucyObject.load
