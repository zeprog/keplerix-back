import secrets
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.authentication import JWTStrategy
from db.models.user import Users
from db.session import get_user_db

class UserManager(IntegerIDMixin, BaseUserManager[Users, int]):
    verification_token_secret = secrets.token_urlsafe(32)
    reset_password_token_secret = secrets.token_urlsafe(32)
    
    async def validate_verification_token(self, token: str) -> Optional[Users]:
        payload = JWTStrategy(secret=self.verification_token_secret).decode(token)
        user_id = payload.get("sub")
        return await self.user_db.get(user_id)

    async def validate_reset_password_token(self, token: str) -> Optional[Users]:
        payload = JWTStrategy(secret=self.reset_password_token_secret).decode(token)
        user_id = payload.get("sub")
        return await self.user_db.get(user_id)

    async def on_after_register(self, user: Users, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: Users, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: Users, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)