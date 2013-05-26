from lucy.models.source import Source
from lucy.models.user import User


def test_basic_source():
    """ Test that source routines works """
    User(_id='joe', name='', email='', gpg='').save()

    p = Source(source='fluxbox',
                version='1.0',
                owner="joe")
    p.save()

    p = Source(source='fluxbox',
                version='2.0',
                owner="joe")
    p.save()

    p = Source(source='frucksbox',
                version='2.0',
                owner="joe")
    x = p.save()

    obj = Source.load(x)
    assert obj['version'] == '2.0'
