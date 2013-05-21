from lucy.envelope import Envelope

tfoo = """Hello: world
Who: me
Where: kruft

foo
bar"""



def test_env_round_trip():
    env = Envelope.load(tfoo)
    assert env['hello'] == 'world'
    assert env['who'] == 'me'
    assert env['Where'] == 'kruft'
    assert env.data == """foo
bar"""
