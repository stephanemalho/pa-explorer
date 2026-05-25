import pytest

from app.security.encryption import decrypt, encrypt


def test_encrypt_returns_string():
    assert isinstance(encrypt("hello"), str)


def test_decrypt_reverses_encrypt():
    assert decrypt(encrypt("hello")) == "hello"


def test_encrypt_is_nondeterministic():
    assert encrypt("hello") != encrypt("hello")


def test_encrypt_empty_string():
    assert decrypt(encrypt("")) == ""


def test_decrypt_invalid_token_raises():
    with pytest.raises(Exception):
        decrypt("not-a-valid-token")
