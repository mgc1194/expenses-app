"""
tests/api/v1/auth/test_login.py — Tests for POST /auth/login.

auth/conftest.py provides: client, valid_payload, registered_user.
"""

import pytest


@pytest.mark.django_db
class TestAuthLogin:
    @pytest.fixture(autouse=True)
    def mock_login(self, mocker):
        """Patch Django's login() to avoid session handling in tests."""
        return mocker.patch('api.v1.auth.login')

    def test_successful_login_returns_user(self, client, valid_payload, registered_user):
        response = client.post(
            '/auth/login',
            json={'email': valid_payload['email'], 'password': valid_payload['password']},
        )
        assert response.status_code == 200
        assert response.json()['email'] == valid_payload['email']

    def test_wrong_password_returns_401(self, client, registered_user, valid_payload):
        response = client.post(
            '/auth/login',
            json={'email': valid_payload['email'], 'password': 'WrongPassword1!'},
        )
        assert response.status_code == 401

    def test_unknown_email_returns_401(self, client):
        response = client.post(
            '/auth/login',
            json={'email': 'nobody@example.com', 'password': 'SomePassword1!'},
        )
        assert response.status_code == 401

    def test_login_email_is_case_insensitive(self, client, valid_payload, registered_user):
        response = client.post(
            '/auth/login',
            json={'email': valid_payload['email'].upper(), 'password': valid_payload['password']},
        )
        assert response.status_code == 200

    def test_error_message_does_not_distinguish_email_from_password(
        self, client, registered_user, valid_payload
    ):
        """Ensures identical error messages for wrong email vs wrong password
        to prevent user enumeration attacks."""
        wrong_email = client.post(
            '/auth/login',
            json={'email': 'nobody@example.com', 'password': valid_payload['password']},
        )
        wrong_password = client.post(
            '/auth/login',
            json={'email': valid_payload['email'], 'password': 'WrongPassword1!'},
        )
        assert wrong_email.json()['detail'] == wrong_password.json()['detail']
