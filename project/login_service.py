from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
import prisma
import prisma.models
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    Produces a JWT token for session management if the credentials are verified correctly.
    """

    token: str


async def login(username: str, password: str) -> LoginResponse:
    """
    Authenticates a user, allowing them to log into the system. It accepts credentials, such as username
    and password, verifies them against the stored data, and returns a JWT token for session management if
    the credentials are correct.

    Args:
        username (str): The username of the user trying to login. This can be an email or a user-registered name.
        password (str): The password for the given username, used for authentication purposes.

    Returns:
        LoginResponse: Produces a JWT token for session management if the credentials are verified correctly.

    Example:
        username = 'user@example.com'
        password = 'SecurePassword123'
        response = login(username, password)
        print(response.token)  # Outputs the JWT token if credentials are correct.
    """
    user: Optional[prisma.models.User] = await prisma.models.User.prisma().find_unique(
        where={"email": username}
    )
    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise ValueError("Invalid username or password")
    jwt_payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    jwt_token = jwt.encode(jwt_payload, "your-256-bit-secret", algorithm="HS256")
    return LoginResponse(token=jwt_token)
