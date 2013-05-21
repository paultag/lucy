from lucy.models import LucyObject


class LucyFord(LucyObject):
    _type = 'test'


def test_basic_actions():
    """ Test that basic save / load works. """

    lo = LucyFord()
    lo['foo'] = 'bar'
    uid = lo.save()

    obj = LucyFord.load(uid)
    obj.pop('updated_at')
    obj.pop('created_at')
    lo.pop('updated_at')
    lo.pop('created_at')
    assert obj == lo, "Make sure loaded object == generated object"
    obj['bar'] = 'baz'
    assert obj != lo, "Make sure loaded object != generated object"

    obj.save()
    lo = obj
    obj = LucyFord.load(uid)

    obj.pop('updated_at')
    lo.pop('updated_at')

    assert obj == lo, "Make sure loaded object == generated object"

    assert len(list(LucyFord.query({}))) == 1, "Count sucks"
    obj.delete()
    assert len(list(LucyFord.query({}))) == 0, "Count sucks post remove"

    try:
        obj = LucyFord.load("INVALID")
        assert True is False, "Invalid query went through"
    except KeyError:
        pass
