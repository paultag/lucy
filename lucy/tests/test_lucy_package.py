from lucy.models.package import Package


def test_basic_package():
    """ Test that package routines works """

    p = Package(source='fluxbox',
                version='1.0',
                owner=None)
    p.save()

    p = Package(source='fluxbox',
                version='2.0',
                owner=None)
    p.save()

    p = Package(source='frucksbox',
                version='2.0',
                owner=None)
    x = p.save()

    assert len(list(Package.get_all_versions("fluxbox"))) == 2
    assert len(list(Package.get_all_versions("frucksbox"))) == 1

    obj = Package.load(x)
    assert obj['version'] == '2.0'
