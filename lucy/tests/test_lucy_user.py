from lucy.models.user import User


def test_basic_user_foo():
    """ Test that user routines works """

    u = User(_id='joe',
             name='Joe Bar',
             gpg="8F049AD82C92066C7352D28A7B585B30807C2A87",
             email="noreply@example.com")

    assert 'joe' == u.save()
    u.save()

    joe = User.get_by_email('noreply@example.com')

    joe.pop('updated_at')
    u.pop('updated_at')

    assert joe == u

    joe = User.get_by_key("8F049AD82C92066C7352D28A7B585B30807C2A87")

    joe.pop('updated_at')

    assert joe == u

    try:
        joe = User.get_by_key("foo")
        assert True is False, "KeyCheck failed"
    except KeyError:
        pass
