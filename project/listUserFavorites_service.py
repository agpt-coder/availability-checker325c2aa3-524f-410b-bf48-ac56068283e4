from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class ProfessionalInfo(BaseModel):
    """
    Basic contact information of a professional.
    """

    professional_id: int
    email: str
    specialty: str


class FavoritesResponse(BaseModel):
    """
    Response model returning a list of favorite professionals with basic contact information.
    """

    favorites: List[ProfessionalInfo]


async def listUserFavorites(user_id: int) -> FavoritesResponse:
    """
    Lists all favorite professionals of the user, pulled from their profile. Includes professional IDs and basic contact info. Useful for quickly accessing preferred professionals.

    Args:
    user_id (int): The unique identifier of the user for whom to retrieve favorite professionals.

    Returns:
    FavoritesResponse: Response model returning a list of favorite professionals with basic contact information.
    """
    profile = await prisma.models.Profile.prisma().find_unique(
        where={"userId": user_id}, include={"favorites": True}
    )
    if not profile:
        return FavoritesResponse(favorites=[])
    favorite_professionals = [
        ProfessionalInfo(
            professional_id=prof.id, email=prof.email, specialty=prof.specialty
        )
        for prof in profile.favorites
    ]
    return FavoritesResponse(favorites=favorite_professionals)
