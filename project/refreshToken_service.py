import datetime

import jwt
import prisma
import prisma.models
from pydantic import BaseModel


class RefreshTokenResponse(BaseModel):
    """
    Provides a new authentication token for the user, ensuring continued access without re-login.
    """

    new_token: str


JWT_SECRET = "your_jwt_secret"

JWT_ALGORITHM = "HS256"


async def refreshToken(token: str) -> RefreshTokenResponse:
    """
    Refreshes the authentication token when the current token is about to expire. This endpoint requires a valid, non-expired token and returns a new token for continued use, ensuring the user remains authenticated without needing to log in again.

    Args:
        token (str): The current valid, non-expired authentication token provided by the user.

    Returns:
        RefreshTokenResponse: Provides a new authentication token for the user, ensuring continued access without re-login.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    user_id = payload["user_id"]
    user = await prisma.models.User.prisma().find_unique(where={"id": user_id})
    if user is None:
        raise ValueError("User not found")
    new_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    new_token = jwt.encode(new_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return RefreshTokenResponse(new_token=new_token)
