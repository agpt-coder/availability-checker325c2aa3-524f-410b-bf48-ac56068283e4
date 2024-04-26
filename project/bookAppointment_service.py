from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class BookingResponse(BaseModel):
    """
    Response model for the booking process. It provides details on the success or failure of the booking and, in case of success, the booking details.
    """

    bookingId: Optional[int] = None
    status: str
    message: str


async def bookAppointment(
    userId: int, professionalId: int, slotId: int
) -> BookingResponse:
    """
    Accepts user-selected time slots and professional details and sends this info to the Schedule Management System for processing and confirming the booking. This function performs validations to ensure the slot is still available and compatible with the professional’s schedule, using transaction mechanisms to maintain consistency. Expect confirmation of booking or error message in response.

    Args:
        userId (int): The ID of the user who is making a booking.
        professionalId (int): The ID of the professional whose slot is being booked.
        slotId (int): The ID of the slot that is being attempted to book.

    Returns:
        BookingResponse: Response model for the booking process. It provides details on the success or failure of the booking and, in case of success, the booking details.
    """
    slot = await prisma.models.Slot.prisma().find_unique(
        where={"id": slotId}, include={"professional": True, "bookings": True}
    )
    if not slot or not slot.isActive or slot.professionalId != professionalId:
        return BookingResponse(
            status="error", message="Invalid slot or mismatch of professional ID"
        )
    if any(
        (
            booking.status == prisma.enums.BookingStatus.CONFIRMED
            for booking in slot.bookings
        )
    ):
        return BookingResponse(status="error", message="Slot is already booked")
    new_booking = await prisma.models.Booking.prisma().create(
        data={
            "userId": userId,
            "slotId": slotId,
            "status": prisma.enums.BookingStatus.PENDING,
        }
    )
    if new_booking:
        return BookingResponse(
            bookingId=new_booking.id,
            status="pending",
            message="Booking placed and is pending confirmation",
        )
    return BookingResponse(status="error", message="Failed to place booking")
