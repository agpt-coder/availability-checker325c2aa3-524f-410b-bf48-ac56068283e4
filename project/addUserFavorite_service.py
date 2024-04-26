from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class Professional(BaseModel):
    """
    Object type representing a professional, including ID, email, and specialty details.
    """

    id: int
    email: str
    specialty: str


class AddFavoriteResponse(BaseModel):
    """
    Response model for POST /user/favorites. Returns the updated list of favorite professionals.
    """

    favorites: List[Professional]


async def addUserFavorite(professional_id: int) -> AddFavoriteResponse:
    """
    Adds a professional to the user's list of favorites. Requires the professional's ID. Returns updated list of favorites.

    Args:
        professional_id (int): ID of the professional to be added to the user's list of favorites.

    Returns:
        AddFavoriteResponse: Response model for POST /user/favorites. Returns the updated list of favorite professionals.

    Example:
        pro_id = 3
        response = addUserFavorite(pro_id)
        > AddFavoriteResponse(favorites=[...])  # Assuming there are already some favorites in the list
    """
    current_user_id = 1
    professional = await prisma.models.Professional.prisma().find_unique(
        where={"id": professional_id}
    )
    if not professional:
        raise ValueError("Professional with the provided ID does not exist.")
    await prisma.models.Profile.prisma().update(
        where={"userId": current_user_id},
        data={"favorites": {"connect": {"id": professional_id}}},
    )
    updated_profile = await prisma.models.Profile.prisma().find_unique(
        where={"userId": current_user_id}, include={"favorites": True}
    )
    favorites_list = [
        Professional(id=fav.id, email=fav.email, specialty=fav.specialty)
        for fav in updated_profile.favorites
    ]
    response = AddFavoriteResponse(favorites=favorites_list)
    return response
