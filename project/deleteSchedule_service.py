import datetime

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class DeleteScheduleResponse(BaseModel):
    """
    Communicates the result of the schedule deletion operation. Includes message of operation's success or failure.
    """

    success: bool
    message: str


async def deleteSchedule(
    scheduleId: int, requesterRole: prisma.enums.Role
) -> DeleteScheduleResponse:
    """
    Removes a schedule entry from the system using the schedule ID. This operation must ensure that it cleans up all associated data and releases any booked resources or slots. Notifications are sent to affected parties to advise them of the cancellation.

    Args:
    scheduleId (int): The identifier for the schedule to be removed.
    requesterRole (prisma.enums.Role): The role of the person making the request. Must be either Admin or Professional.

    Returns:
    DeleteScheduleResponse: Communicates the result of the schedule deletion operation. Includes message of operation's success or failure.
    """
    if requesterRole not in [prisma.enums.Role.ADMIN, prisma.enums.Role.PROFESSIONAL]:
        return DeleteScheduleResponse(
            success=False,
            message="Unauthorized access. Only Admin or Professional can delete schedules.",
        )
    slot = await prisma.models.Slot.prisma().find_unique(where={"id": scheduleId})
    if not slot:
        return DeleteScheduleResponse(success=False, message="Schedule not found.")
    bookings = await prisma.models.Booking.prisma().find_many(
        where={
            "slotId": scheduleId,
            "status": {"not": prisma.enums.BookingStatus.CANCELLED},
        }
    )
    for booking in bookings:
        await prisma.models.Booking.prisma().update(
            where={"id": booking.id},
            data={"status": prisma.enums.BookingStatus.CANCELLED},
        )
        notification_message = (
            f"Your booking for slot starting at {slot.startTime} has been cancelled."
        )
        await prisma.models.Notification.prisma().create(
            data={
                "userId": booking.userId,
                "message": notification_message,
                "createdAt": datetime.datetime.now(),
                "read": False,
            }
        )
    if all(
        (booking.status == prisma.enums.BookingStatus.CANCELLED for booking in bookings)
    ):
        await prisma.models.Slot.prisma().delete(where={"id": scheduleId})
        return DeleteScheduleResponse(
            success=True,
            message="Schedule deleted successfully with all booked slots released and notifications sent.",
        )
    return DeleteScheduleResponse(
        success=False, message="Unable to fully delete schedule due to active bookings."
    )
