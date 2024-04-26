from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class UserProfileUpdateResponse(BaseModel):
    """
    This model returns the updated details of the user's profile to confirm changes have been stored.
    """

    userId: int
    email: str
    favorites: List[int]


async def updateUserProfile(
    userId: int, email: str, favorites: List[int]
) -> UserProfileUpdateResponse:
    """
    Updates user-specific information such as email or favorite professionals. Requires current user data and the modifications. Returns the updated user profile.

    Args:
        userId (int): The unique identifier of the user to be updated.
        email (str): The new or updated email address of the user.
        favorites (List[int]): List of IDs of the professionals marked as favorite by the user.

    Returns:
        UserProfileUpdateResponse: This model returns the updated details of the user's profile to confirm changes have been stored.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId}, include={"profiles": True}
    )
    if user is None:
        raise ValueError("User not found")
    updated_user = await prisma.models.User.prisma().update(
        where={"id": userId},
        data={
            "email": email,
            "profiles": {
                "update": {
                    "favorites": {"set": [{"id": fav_id} for fav_id in favorites]}
                }
            },
        },
        include={"profiles": {"include": {"favorites": True}}},
    )
    updated_profile = updated_user.profiles[0]
    favorites_ids = [f.id for f in updated_profile.favorites]
    return UserProfileUpdateResponse(
        userId=userId, email=email, favorites=favorites_ids
    )
