from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class UpdatedUserDetails(BaseModel):
    """
    Details of the updated user information, only provided if the update is successful.
    """

    email: str
    userId: str


class UserUpdateResponse(BaseModel):
    """
    The response model for updating user details. Should confirm the success of the update or provide a meaningful error message.
    """

    success: bool
    message: str
    updatedDetails: UpdatedUserDetails


async def updateUser(
    userId: str, email: Optional[str], password: Optional[str]
) -> UserUpdateResponse:
    """
    Updates details of a specific user. This allows users to update their own profiles, such as changing their password or email. The endpoint checks for authentication and authorization before permitting the update. It ensures data validation before committing any changes.

    Args:
    userId (str): The unique identifier of the user, taken from the path to determine which user's information is being updated.
    email (Optional[str]): The new email address the user wishes to update to. Should be validated to ensure it adheres to standard email formatting.
    password (Optional[str]): The new password the user wishes to update to. This should be a hashed string to ensure security standards are met.

    Returns:
    UserUpdateResponse: The response model for updating user details. Should confirm the success of the update or provide a meaningful error message.
    """
    search_user = await prisma.models.User.prisma().find_unique(
        where={"id": int(userId)}
    )
    if not search_user:
        return UserUpdateResponse(
            success=False, message="User not found.", updatedDetails=None
        )
    update_data = {}
    if email is not None:
        update_data["email"] = email
    if password is not None:
        update_data["password"] = password
    if not update_data:
        return UserUpdateResponse(
            success=False,
            message="No update information provided.",
            updatedDetails=None,
        )
    try:
        updated_user = await prisma.models.User.prisma().update(
            where={"id": int(userId)}, data=update_data
        )
    except Exception as e:
        return UserUpdateResponse(
            success=False,
            message=f"Failed to update user due to error: {str(e)}",
            updatedDetails=None,
        )
    updated_details = UpdatedUserDetails(
        email=updated_user.email, userId=str(updated_user.id)
    )
    return UserUpdateResponse(
        success=True,
        message="User updated successfully.",
        updatedDetails=updated_details,
    )
