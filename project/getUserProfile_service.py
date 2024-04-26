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


async def getUserProfile(user_id: int) -> UserProfileResponse:
    """
    Retrieves the user profile data including booked appointments and favorite professionals.
    It integrates with the Schedule Management to pull the latest booking details. Response
    includes user ID, name, email, booked appointments, and favorites list.

    Args:
        user_id (int): The unique identifier of the user whose profile details are being retrieved.

    Returns:
        UserProfileResponse: Provides detailed user profile information including both personal details
                             and professional affiliations like booked appointments and favorite professionals.
    """
    user_profile = await prisma.models.Profile.prisma().find_first(
        where={"userId": user_id}, include={"user": True, "favorites": True}
    )
    if user_profile is None:
        return UserProfileResponse(
            user_id=user_id, name="", email="", booked_appointments=[], favorites=[]
        )
    user = user_profile.user
    name = f"{user_profile.firstName} {user_profile.lastName}"
    email = user.email
    booked_appointments = []
    for booking in user.bookings:
        booked_appointments.append(
            BookingOverview(
                booking_id=booking.id,
                datetime=booking.slot.startTime,
                status=booking.status.name,
                professional_name=booking.slot.professional.email,
            )
        )
    favorites = []
    for favorite in user_profile.favorites:
        favorites.append(
            ProfessionalMini(
                professional_id=favorite.id,
                name=favorite.email,
                specialty=favorite.specialty,
            )
        )
    return UserProfileResponse(
        user_id=user_id,
        name=name,
        email=email,
        booked_appointments=booked_appointments,
        favorites=favorites,
    )
