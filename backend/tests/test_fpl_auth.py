import base64
import json
import time
from unittest.mock import AsyncMock, patch, mock_open
import pytest
from app.clients.fpl_auth import is_jwt_expired, get_jwt_token


def make_fake_jwt(exp: int) -> str:
    header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().replace("=", "")
    payload = base64.b64encode(json.dumps({"exp": exp}).encode()).decode().replace("=", "")
    return f"{header}.{payload}.signature"


def test_is_jwt_expired() -> None:
    # Future expiration (valid)
    valid_token = make_fake_jwt(int(time.time()) + 1000)
    assert not is_jwt_expired(valid_token)

    # Past expiration (expired)
    expired_token = make_fake_jwt(int(time.time()) - 1000)
    assert is_jwt_expired(expired_token)

    # Near expiration (within the 5-minute safety buffer)
    near_expired_token = make_fake_jwt(int(time.time()) + 100)
    assert is_jwt_expired(near_expired_token)

    # Invalid formats
    assert is_jwt_expired("invalid.token")
    assert is_jwt_expired("")


@pytest.mark.anyio
async def test_get_jwt_token_cached_valid() -> None:
    valid_token = make_fake_jwt(int(time.time()) + 1000)
    mock_data = json.dumps({"token": valid_token, "cached_at": time.time()})

    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_data)):
        token = await get_jwt_token()
        assert token == valid_token


@pytest.mark.anyio
@patch("app.clients.fpl_auth.async_login")
async def test_get_jwt_token_expired_relogin(mock_async_login: AsyncMock) -> None:
    expired_token = make_fake_jwt(int(time.time()) - 1000)
    new_token = make_fake_jwt(int(time.time()) + 1000)
    mock_data = json.dumps({"token": expired_token, "cached_at": time.time()})
    mock_async_login.return_value = new_token

    # Mock file reading of old token, then write of new token
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_data)), \
         patch("pathlib.Path.mkdir"):
        token = await get_jwt_token()
        assert token == new_token
        mock_async_login.assert_called_once()
