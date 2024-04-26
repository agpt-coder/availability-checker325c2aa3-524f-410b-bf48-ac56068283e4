from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class Notification(BaseModel):
    """
    Model representing the system notifications related to user and administrative events.
    """

    id: int
    userId: int
    message: str
    createdAt: datetime
    read: bool


class UpdateScheduleResponse(BaseModel):
    """
    Confirms the successful update of the schedule with revised details. It also includes any notification details sent as a result of the update.
    """

    updated: bool
    scheduleId: int
    notification: Notification


async def updateSchedule(
    scheduleId: int,
    startTime: datetime,
    endTime: datetime,
    professionalId: int,
    activity: str,
) -> UpdateScheduleResponse:
    """
    Updates an existing schedule entry identified by the schedule ID. It requires complete or partial schedule details for updates such as changing the time slot, modifying the associated activity, or altering the professional linked with the schedule entry. Each update sends a notification via the Notification Engine to inform relevant stakeholders of the schedule change.

    Args:
    scheduleId (int): Unique identifier for the schedule that needs updating.
    startTime (datetime): Optional updated start time for the schedule.
    endTime (datetime): Optional updated end time for the schedule.
    professionalId (int): Optional professional identifier if the schedule is being reassigned to a different professional.
    activity (str): Description of the activity involved in this schedule, can be updated.

    Returns:
    UpdateScheduleResponse: Confirms the successful update of the schedule with revised details. It also includes any notification details sent as a result of the update.
    """
    slot = await prisma.models.Slot.prisma().find_unique(where={"id": scheduleId})
    if not slot:
        return UpdateScheduleResponse(
            updated=False,
            scheduleId=scheduleId,
            notification=Notification(
                id=-1,
                userId=-1,
                message="Schedule Not Found",
                createdAt=datetime.now(),
                read=False,
            ),
        )
    updated_slot = await prisma.models.Slot.prisma().update(
        where={"id": scheduleId},
        data={
            "startTime": startTime,
            "endTime": endTime,
            "professionalId": professionalId,
        },
    )
    notification = await prisma.models.Notification.prisma().create(
        data={
            "userId": professionalId,
            "message": f"Schedule updated: {activity}",
            "createdAt": datetime.now(),
            "read": False,
        }
    )
    notification_model = Notification(
        id=notification.id,
        userId=notification.userId,
        message=notification.message,
        createdAt=notification.createdAt,
        read=notification.read,
    )
    return UpdateScheduleResponse(
        updated=True, scheduleId=scheduleId, notification=notification_model
    )
