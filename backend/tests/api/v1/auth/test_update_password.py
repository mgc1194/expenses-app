"""
tests/api/v1/auth/test_update_password.py — Tests for POST /auth/me/password.

auth/conftest.py provides: client, registered_user, valid_payload.
"""

import pytest

VALID_NEW_PASSWORD = 'NewSecure@Password1!'


@pytest.mark.django_db
class TestUpdatePassword:
    @pytest.fixture(autouse=True)
    def mock_update_session_auth_hash(self, mocker):
        """Patch update_session_auth_hash to avoid session handling in tests.

        Ninja's TestClient uses a mock HttpRequest with no session attribute,
        so update_session_auth_hash raises AttributeError without this patch.
        The session-remains-valid test asserts on this mock directly.
        """
        return mocker.patch('api.v1.auth.update_session_auth_hash')

    # ── Auth ──────────────────────────────────────────────────────────────────

    def test_unauthenticated_request_returns_401(self, client):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': 'anything',
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
        )
        assert response.status_code == 401

    # ── Success ───────────────────────────────────────────────────────────────

    def test_successful_password_change_returns_204(self, client, registered_user, valid_payload):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
            user=registered_user,
        )
        assert response.status_code == 204

    def test_password_is_changed_in_database(self, client, registered_user, valid_payload):
        client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
            user=registered_user,
        )
        registered_user.refresh_from_db()
        assert registered_user.check_password(VALID_NEW_PASSWORD)

    def test_session_remains_valid_after_password_change(
        self, client, registered_user, valid_payload, mock_update_session_auth_hash
    ):
        # The autouse fixture patches update_session_auth_hash; assert it was
        # called so we know the endpoint keeps the session alive after a change.
        client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
            user=registered_user,
        )
        assert mock_update_session_auth_hash.called

    # ── Current password validation ───────────────────────────────────────────

    def test_wrong_current_password_returns_400(self, client, registered_user):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': 'WrongPassword1!',
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
            user=registered_user,
        )
        assert response.status_code == 400
        assert 'current password is incorrect' in response.json()['detail'].lower()

    def test_wrong_current_password_does_not_change_password(
        self, client, registered_user, valid_payload
    ):
        client.post(
            '/auth/me/password',
            json={
                'current_password': 'WrongPassword1!',
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': VALID_NEW_PASSWORD,
            },
            user=registered_user,
        )
        registered_user.refresh_from_db()
        assert registered_user.check_password(valid_payload['password'])

    # ── New password validation ───────────────────────────────────────────────

    def test_mismatched_new_passwords_returns_400(self, client, registered_user, valid_payload):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': VALID_NEW_PASSWORD,
                'confirm_new_password': 'DifferentPassword1!',
            },
            user=registered_user,
        )
        assert response.status_code == 400
        assert 'do not match' in response.json()['detail'].lower()

    def test_weak_new_password_too_short_returns_400(self, client, registered_user, valid_payload):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': 'Short1!',
                'confirm_new_password': 'Short1!',
            },
            user=registered_user,
        )
        assert response.status_code == 400

    def test_weak_new_password_all_numeric_returns_400(
        self, client, registered_user, valid_payload
    ):
        response = client.post(
            '/auth/me/password',
            json={
                'current_password': valid_payload['password'],
                'new_password': '12345678901234',
                'confirm_new_password': '12345678901234',
            },
            user=registered_user,
        )
        assert response.status_code == 400
