"""
tests/api/v1/auth/test_me.py — Tests for GET /auth/me.

auth/conftest.py provides: client, registered_user.
"""

import pytest


@pytest.mark.django_db
class TestAuthMe:
    def test_unauthenticated_me_returns_401(self, client):
        response = client.get('/auth/me')
        assert response.status_code == 401

    def test_authenticated_me_returns_user(self, client, registered_user):
        response = client.get('/auth/me', user=registered_user)
        assert response.status_code == 200
        assert response.json()['email'] == registered_user.email
