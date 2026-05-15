"""
tests/api/v1/auth/test_logout.py — Tests for POST /auth/logout.

auth/conftest.py provides: client, registered_user.
"""

import pytest


@pytest.mark.django_db
class TestAuthLogout:
    @pytest.fixture(autouse=True)
    def mock_logout(self, mocker):
        """Patch Django's logout() to avoid session handling in tests."""
        return mocker.patch('api.v1.auth.logout')

    def test_unauthenticated_logout_returns_401(self, client):
        response = client.post('/auth/logout')
        assert response.status_code == 401

    def test_authenticated_logout_returns_success(self, client, registered_user):
        response = client.post('/auth/logout', user=registered_user)
        assert response.status_code == 200
