import pytest
from src.api.dependencies import create_access_token
from jose import jwt
def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "user123"})
    payload = jwt.decode(token,key="", options={"verify_signature": False})
    assert payload["sub"] == "user123"
    assert "exp" in payload
