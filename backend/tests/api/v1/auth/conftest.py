"""
tests/api/v1/auth/conftest.py — Shared fixtures for auth endpoint tests.

Auth tests use only their own fixtures (no shared user/household state needed).
"""

import pytest
from ninja.testing import TestClient

from api.v1.auth import router
from users.models import CustomUser


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def valid_payload():
    """A registration payload that passes all validations."""
    return {
        'email': 'john@example.com',
        'password': 'Secure@Password1!',
        'confirm_password': 'Secure@Password1!',
        'first_name': 'John',
        'last_name': 'Doe',
    }


@pytest.fixture
def registered_user(db, valid_payload):
    """A pre-existing user in the database."""
    return CustomUser.objects.create_user(
        username='john',
        email=valid_payload['email'],
        password=valid_payload['password'],
    )
