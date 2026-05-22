"""
schemas/auth.py — API schemas for authentication endpoints.

Schemas define the API contract independently from the database models.
Fields that are internal to the database (e.g. password hashes, internal
flags) are intentionally excluded here.
"""

from ninja import Schema

from schemas.households import HouseholdSchema


class UserSchema(Schema):
    """Output schema for a User.

    Exposes only the fields relevant to the API consumer.
    Password hashes and internal Django fields are not included.
    """

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    households: list[HouseholdSchema]


class RegisterRequest(Schema):
    """Request schema for user registration."""

    email: str
    password: str
    confirm_password: str
    first_name: str = ''
    last_name: str = ''


class LoginRequest(Schema):
    """Request schema for user login."""

    email: str
    password: str


class UpdateProfileRequest(Schema):
    """Request schema for updating the current user's profile fields.

    All fields are optional — only provided fields are updated.
    Omitted fields are left unchanged on the user record.
    """

    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None


class UpdatePasswordRequest(Schema):
    """Request schema for changing the current user's password."""

    current_password: str
    new_password: str
    confirm_new_password: str


class MessageResponse(Schema):
    """Generic message response for simple confirmations."""

    message: str
