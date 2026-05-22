"""
tests/api/v1/auth/test_update_profile.py — Tests for PATCH /auth/me.

auth/conftest.py provides: client, registered_user.
"""

import pytest

from users.models import CustomUser


@pytest.mark.django_db
class TestUpdateProfile:
    # ── Auth ──────────────────────────────────────────────────────────────────

    def test_unauthenticated_request_returns_401(self, client):
        response = client.patch('/auth/me', json={})
        assert response.status_code == 401

    # ── No-op ─────────────────────────────────────────────────────────────────

    def test_empty_payload_returns_current_user_unchanged(self, client, registered_user):
        response = client.patch('/auth/me', json={}, user=registered_user)
        assert response.status_code == 200
        data = response.json()
        assert data['email'] == registered_user.email
        assert data['username'] == registered_user.username

    # ── Individual field updates ──────────────────────────────────────────────

    def test_update_first_name(self, client, registered_user):
        response = client.patch('/auth/me', json={'first_name': 'Jane'}, user=registered_user)
        assert response.status_code == 200
        assert response.json()['first_name'] == 'Jane'

    def test_update_last_name(self, client, registered_user):
        response = client.patch('/auth/me', json={'last_name': 'Doe'}, user=registered_user)
        assert response.status_code == 200
        assert response.json()['last_name'] == 'Doe'

    def test_update_username(self, client, registered_user):
        response = client.patch('/auth/me', json={'username': 'newusername'}, user=registered_user)
        assert response.status_code == 200
        assert response.json()['username'] == 'newusername'

    def test_update_email(self, client, registered_user):
        response = client.patch('/auth/me', json={'email': 'new@example.com'}, user=registered_user)
        assert response.status_code == 200
        assert response.json()['email'] == 'new@example.com'

    # ── All fields at once ────────────────────────────────────────────────────

    def test_update_all_fields(self, client, registered_user):
        payload = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith',
            'email': 'jane@example.com',
        }
        response = client.patch('/auth/me', json=payload, user=registered_user)
        assert response.status_code == 200
        data = response.json()
        assert data['first_name'] == 'Jane'
        assert data['last_name'] == 'Smith'
        assert data['username'] == 'janesmith'
        assert data['email'] == 'jane@example.com'

    # ── Email validation ──────────────────────────────────────────────────────

    def test_email_normalised_to_lowercase(self, client, registered_user):
        response = client.patch('/auth/me', json={'email': 'NEW@EXAMPLE.COM'}, user=registered_user)
        assert response.status_code == 200
        assert response.json()['email'] == 'new@example.com'

    def test_invalid_email_format_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'email': 'notanemail'}, user=registered_user)
        assert response.status_code == 400

    def test_duplicate_email_returns_400(self, client, registered_user, db):
        other = CustomUser.objects.create_user(
            username='other',
            email='other@example.com',
            password='Password1!',
        )
        response = client.patch('/auth/me', json={'email': other.email}, user=registered_user)
        assert response.status_code == 400
        assert 'email already exists' in response.json()['detail'].lower()

    def test_same_email_as_self_is_accepted(self, client, registered_user):
        """Updating email to the current value should succeed (no false uniqueness error)."""
        response = client.patch(
            '/auth/me', json={'email': registered_user.email}, user=registered_user
        )
        assert response.status_code == 200

    def test_blank_email_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'email': '   '}, user=registered_user)
        assert response.status_code == 400

    # ── Username validation ───────────────────────────────────────────────────

    def test_duplicate_username_returns_400(self, client, registered_user, db):
        other = CustomUser.objects.create_user(
            username='takenusername',
            email='other2@example.com',
            password='Password1!',
        )
        response = client.patch('/auth/me', json={'username': other.username}, user=registered_user)
        assert response.status_code == 400
        assert 'username is already taken' in response.json()['detail'].lower()

    def test_same_username_as_self_is_accepted(self, client, registered_user):
        """Updating username to the current value should succeed."""
        response = client.patch(
            '/auth/me', json={'username': registered_user.username}, user=registered_user
        )
        assert response.status_code == 200

    def test_username_over_150_chars_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'username': 'a' * 151}, user=registered_user)
        assert response.status_code == 400

    def test_invalid_username_characters_returns_400(self, client, registered_user):
        response = client.patch(
            '/auth/me', json={'username': 'invalid username!'}, user=registered_user
        )
        assert response.status_code == 400

    def test_blank_username_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'username': '   '}, user=registered_user)
        assert response.status_code == 400

    # ── Name validation ───────────────────────────────────────────────────────

    def test_blank_first_name_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'first_name': '   '}, user=registered_user)
        assert response.status_code == 400

    def test_blank_last_name_returns_400(self, client, registered_user):
        response = client.patch('/auth/me', json={'last_name': '   '}, user=registered_user)
        assert response.status_code == 400

    # ── Persistence ───────────────────────────────────────────────────────────

    def test_changes_persisted_to_database(self, client, registered_user):
        client.patch('/auth/me', json={'first_name': 'Persisted'}, user=registered_user)
        registered_user.refresh_from_db()
        assert registered_user.first_name == 'Persisted'

    # ── Concurrent update race ─────────────────────────────────────────────────

    def test_concurrent_duplicate_email_returns_specific_400(
        self, client, registered_user, db, mocker
    ):
        # Another user claims the email between our exists() check and save().
        # Patch only CustomUser.save in the auth module so other.save() inside
        # the side-effect is not intercepted (avoids infinite recursion).
        other = CustomUser.objects.create_user(
            username='other', email='race@example.com', password='Password1!'
        )
        from django.db import IntegrityError

        def _steal_then_fail(*args, **kwargs):
            CustomUser.objects.filter(pk=other.pk).update(email='race@example.com')
            raise IntegrityError('Duplicate entry')

        mocker.patch('api.v1.auth.CustomUser.save', side_effect=_steal_then_fail)
        response = client.patch(
            '/auth/me', json={'email': 'race@example.com'}, user=registered_user
        )
        assert response.status_code == 400
        assert 'email already exists' in response.json()['detail'].lower()

    def test_concurrent_duplicate_username_returns_specific_400(
        self, client, registered_user, db, mocker
    ):
        # Another user claims the username between our exists() check and save().
        # Patch only CustomUser.save in the auth module so other.save() inside
        # the side-effect is not intercepted (avoids infinite recursion).
        other = CustomUser.objects.create_user(
            username='other', email='other3@example.com', password='Password1!'
        )
        from django.db import IntegrityError

        def _steal_then_fail(*args, **kwargs):
            CustomUser.objects.filter(pk=other.pk).update(username='racename')
            raise IntegrityError('Duplicate entry')

        mocker.patch('api.v1.auth.CustomUser.save', side_effect=_steal_then_fail)
        response = client.patch('/auth/me', json={'username': 'racename'}, user=registered_user)
        assert response.status_code == 400
        assert 'username is already taken' in response.json()['detail'].lower()

    def test_unidentified_integrity_error_returns_generic_400(
        self, client, registered_user, mocker
    ):
        # IntegrityError on a non-email/username field falls back to the generic message.
        from django.db import IntegrityError

        mocker.patch(
            'api.v1.auth.CustomUser.save',
            side_effect=IntegrityError('Duplicate entry on unknown column'),
        )
        response = client.patch('/auth/me', json={'first_name': 'Test'}, user=registered_user)
        assert response.status_code == 400
        assert 'conflicting value' in response.json()['detail'].lower()
