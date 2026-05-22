"""
schemas/auth.py — API schemas for authentication endpoints.
"""

from ninja import Schema

from schemas.households import HouseholdSchema


class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    households: list[HouseholdSchema]


class RegisterRequest(Schema):
    email: str
    password: str
    confirm_password: str
    first_name: str = ''
    last_name: str = ''


class LoginRequest(Schema):
    email: str
    password: str


class UpdateProfileRequest(Schema):
    """Request schema for updating the current user's profile fields.
    All fields are optional — only provided fields are updated.
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
    message: str
