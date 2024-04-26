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


async def fetch_full_user_profile(user_id: int) -> UserProfileResponse:
    user = await prisma.models.User.prisma().find_unique(
        where={"id": user_id}, include={"profiles": True, "bookings": True}
    )
    if not user:
        raise ValueError("prisma.models.User not found!")
    profile = user.profiles[0] if user.profiles else None
    booked_appointments = [
        BookingOverview(
            booking_id=b.id,
            datetime=b.slot.startTime,
            status=b.status.name,
            professional_name=b.slot.professional.email,
        )
        for b in user.bookings
    ]
    favorites = [
        ProfessionalMini(professional_id=p.id, name=p.email, specialty=p.specialty)
        for p in profile.favorites
        if profile
    ]
    return UserProfileResponse(
        user_id=user.id,
        name=f"{profile.firstName} {profile.lastName}" if profile else "Unknown",
        email=user.email,
        booked_appointments=booked_appointments,
        favorites=favorites,
    )


async def getUser(userId: int) -> UserProfileResponse:
    """
    Retrieves details of a specific user by their unique identifier (userId). This function uses relational database queries to construct a comprehensive user profile.

    Args:
        userId (int): The unique identifier for the user whose profile is to be retrieved.

    Returns:
        UserProfileResponse: Provides detailed user profile information including keyed details as personal information and professional engagements such as booked appointments and favorite professionals.

    Usage:
        user_profile = await getUser(1)  # Assuming '1' is a valid userId.
        print(user_profile)
    """
    return await fetch_full_user_profile(userId)
