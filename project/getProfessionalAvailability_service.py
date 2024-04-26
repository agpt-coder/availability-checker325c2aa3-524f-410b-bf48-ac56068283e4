from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class FetchAvailabilityRequest(BaseModel):
    """
    Request model for fetching real-time availability data of professionals. As there are no specific request parameters required, this model is kept empty to signify it can handle generic queries for availability.
    """

    pass


class AvailabilityResponse(BaseModel):
    """
    This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable.
    """

    availability: str


async def getProfessionalAvailability(
    request: FetchAvailabilityRequest,
) -> AvailabilityResponse:
    """
    Retrieves real-time availability for a specific professional by their unique ID.
    This function connects to the Schedule Management module to pull detailed availability status
    for the requested professional. Ideal for users needing detailed, individual data.

    Args:
        request (FetchAvailabilityRequest): Request model for fetching real-time availability data of professionals.

    Returns:
        AvailabilityResponse: This model describes the availability state of a professional,
                              indicating if they are currently available, busy, or unavailable.
    """
    professionalId = 1
    current_time = datetime.now()
    slot = await prisma.models.Slot.prisma().find_first(
        where={
            "AND": [
                {"professionalId": {"equals": professionalId}},
                {"startTime": {"lte": current_time}},
                {"endTime": {"gte": current_time}},
                {"isActive": {"equals": True}},
            ]
        }
    )
    if not slot:
        availability_status = "unavailable"
    else:
        booking = await prisma.models.Booking.prisma().find_first(
            where={
                "AND": [
                    {"slotId": {"equals": slot.id}},
                    {"status": {"not": "CANCELLED"}},
                ]
            }
        )
        if booking:
            availability_status = "busy"
        else:
            availability_status = "available"
    response = AvailabilityResponse(availability=availability_status)
    return response
