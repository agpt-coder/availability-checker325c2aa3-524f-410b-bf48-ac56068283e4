from datetime import datetime
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class BookingOverview(BaseModel):
    """
    Summarized details for a booked appointment.
    """

    booking_id: int
    datetime: datetime
    status: prisma.enums.BookingStatus
    professional_name: str


class ProfessionalMini(BaseModel):
    """
    Reduced detail of a Professional entity, for favorites listing.
    """

    professional_id: int
    name: str
    specialty: str


class UserProfileResponse(BaseModel):
    """
    Provides detailed user profile information including both personal details and professional affiliations like booked appointments and favorite professionals.
    """

    user_id: int
    name: str
    email: str
    booked_appointments: List[BookingOverview]
    favorites: List[ProfessionalMini]


async def createUserProfile(
    userId: int, firstName: str, lastName: str, email: str
) -> UserProfileResponse:
    """
    Creates a new user profile with initial details such as user ID, name, and email. Response confirms the creation with the user profile data.

    Args:
        userId (int): Unique identifier of the user for whom the profile is being created.
        firstName (str): First name of the user.
        lastName (str): Last name of the user.
        email (str): Email address of the user; must be unique across all profiles.

    Returns:
        UserProfileResponse: Provides detailed user profile information including both personal details and professional affiliations like booked appointments and favorite professionals.
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        raise ValueError("Email already used by another user.")
    user = await prisma.models.User.prisma().create(
        data={"email": email, "password": "", "role": "REGISTERED_USER"}
    )
    profile = await prisma.models.Profile.prisma().create(
        data={"userId": user.id, "firstName": firstName, "lastName": lastName}
    )
    user_profile_response = UserProfileResponse(
        user_id=user.id,
        name=f"{firstName} {lastName}",
        email=user.email,
        booked_appointments=[],
        favorites=[],
    )
    return user_profile_response
