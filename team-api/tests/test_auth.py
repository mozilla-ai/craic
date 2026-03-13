"""Tests for authentication module."""

import time

import jwt
import pytest
from team_api.auth import create_token, hash_password, verify_password, verify_token


class TestPasswordHashing:
    def test_verify_correct_password(self) -> None:
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed) is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("secret123")
        assert verify_password("wrong", hashed) is False


class TestJWT:
    def test_create_and_verify_token(self) -> None:
        token = create_token("peter", secret="test-secret", ttl_hours=24)
        payload = verify_token(token, secret="test-secret")
        assert payload["sub"] == "peter"

    def test_expired_token_rejected(self) -> None:
        token = create_token("peter", secret="test-secret", ttl_hours=0)
        time.sleep(1)
        with pytest.raises(jwt.ExpiredSignatureError):
            verify_token(token, secret="test-secret")

    def test_invalid_token_rejected(self) -> None:
        with pytest.raises(jwt.DecodeError):
            verify_token("not.a.token", secret="test-secret")

    def test_wrong_secret_rejected(self) -> None:
        token = create_token("peter", secret="secret-a")
        with pytest.raises(jwt.InvalidSignatureError):
            verify_token(token, secret="secret-b")
