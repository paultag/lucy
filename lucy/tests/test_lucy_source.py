from lucy.models.source import Source


def test_basic_source():
    """ Test that source routines works """

    p = Source(source='fluxbox',
                version='1.0',
                owner=None)
    p.save()

    p = Source(source='fluxbox',
                version='2.0',
                owner=None)
    p.save()

    p = Source(source='frucksbox',
                version='2.0',
                owner=None)
    x = p.save()

    assert len(list(Source.get_all_versions("fluxbox"))) == 2
    assert len(list(Source.get_all_versions("frucksbox"))) == 1

    obj = Source.load(x)
    assert obj['version'] == '2.0'
