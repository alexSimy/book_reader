def test_constants_module_importable():
    import src.constants.constants as consts

    assert hasattr(consts, 'MODEL_NAME')
    assert isinstance(consts.MODEL_NAME, str)
    assert hasattr(consts, 'DEFAULT_RESPONSE_TOKENS')
    assert isinstance(consts.DEFAULT_RESPONSE_TOKENS, int)
    assert hasattr(consts, 'DEFAULT_MAX_CHARACTER_PER_CHUNK')
    assert isinstance(consts.DEFAULT_MAX_CHARACTER_PER_CHUNK, int)
