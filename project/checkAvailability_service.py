from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    """
    This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable.
    """

    availability: str


async def checkAvailability(
    professionalId: Optional[int],
    startDate: Optional[datetime],
    endDate: Optional[datetime],
    specialty: Optional[str],
) -> AvailabilityResponse:
    """
    Fetches real-time availability of professionals. It queries the scheduling database to determine available time slots based on professionals’ current activities and schedules. Each query response includes structured data indicating the start and end times of available slots. This endpoint is accessed every time a user wishes to view availability.

    Args:
    professionalId (Optional[int]): Optional path parameter. The unique identifier of the professional to fetch the availability for.
    startDate (Optional[datetime]): Optional query parameter to filter available slots starting from this date.
    endDate (Optional[datetime]): Optional query parameter to filter available slots up to this date.
    specialty (Optional[str]): Optional query parameter to filter availability by professional specialty.

    Returns:
    AvailabilityResponse: This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable.
    """
    query = prisma.models.Professional.prisma().find_many(
        where={
            "id": professionalId,
            "specialty": specialty,
            "availableSlots": {
                "some": {
                    "isActive": True,
                    "startTime": {"gte": startDate} if startDate else None,
                    "endTime": {"lte": endDate} if endDate else None,
                }
            },
        },
        include={"availableSlots": True},
    )
    professionals = await query
    if any((professional.availableSlots for professional in professionals)):
        availability_status = "available"
    else:
        availability_status = "unavailable"
    return AvailabilityResponse(availability=availability_status)
