from typing import Optional

import bcrypt
import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class CreateUserResponse(BaseModel):
    """
    Provides feedback on the result of trying to create a new user, either confirming success or detailing why it failed (e.g. email already in use)
    """

    success: bool
    message: str
    user_id: Optional[int] = None


async def createUser(
    name: str, email: str, password: str, role: prisma.enums.Role
) -> CreateUserResponse:
    """
    Creates a new user account. This endpoint will collect user data such as name, email, and password, and store them securely. The response will confirm the creation of the user or provide error messages for invalid inputs. It uses standard security measures like hashing passwords before storage.

    Args:
        name (str): Full name of the new user.
        email (str): Email address for the new user. Must be unique and valid per standard email format.
        password (str): Password for the new user. This will be hashed before storage for security.
        role (prisma.enums.Role): The role assigned to the user, it should match one of the predefined roles in the prisma.enums.Role enum.

    Returns:
        CreateUserResponse: Provides feedback on the result of trying to create a new user, either confirming success or detailing why it failed (e.g. email already in use).
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        return CreateUserResponse(success=False, message="Email already in use")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    try:
        user = await prisma.models.User.prisma().create(
            data={
                "email": email,
                "password": hashed_password.decode("utf-8"),
                "role": role,
                "profiles": {
                    "create": {
                        "firstName": name.split(" ")[0],
                        "lastName": " ".join(name.split(" ")[1:]),
                    }
                },
            }
        )
        return CreateUserResponse(
            success=True,
            message="prisma.models.User created successfully",
            user_id=user.id,
        )
    except Exception as e:
        return CreateUserResponse(success=False, message=str(e))
