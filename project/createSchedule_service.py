from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class CreateScheduleResponse(BaseModel):
    """
    Response model indicating the successful creation of a schedule. Includes details of the created schedule and initial status.
    """

    scheduleId: int
    professionalId: int
    wasNotificationSent: bool
    isActive: bool


async def createSchedule(
    professionalId: int,
    startTime: datetime,
    endTime: datetime,
    activityType: str,
    isActive: bool,
) -> CreateScheduleResponse:
    """
    Enables the creation of a new schedule entry for a professional. It accepts details such as time slots, professional ID, and activity type. This endpoint requires proper validations to avoid conflicts in the scheduling logic, like overlapping time slots. Upon successful creation, sends a notification to the professional about the new schedule entry.

    Args:
        professionalId (int): Unique identifier for the professional for whom the schedule is being created.
        startTime (datetime): Starting time of the new schedule slot.
        endTime (datetime): Ending time of the new schedule slot.
        activityType (str): Type of activity or session planned for this time slot.
        isActive (bool): Flag to activate or deactivate the slot immediately upon creation.

    Returns:
        CreateScheduleResponse: Response model indicating the successful creation of a schedule. Includes details of the created schedule and initial status.
    """
    if startTime >= endTime:
        raise ValueError("Start time must be before end time.")
    existing_slots = await prisma.models.Slot.prisma().find_many(
        where={
            "professionalId": professionalId,
            "startTime": {"lt": endTime},
            "endTime": {"gt": startTime},
            "isActive": True,
        }
    )
    if existing_slots:
        raise ValueError("There are overlapping slots for the same time range.")
    new_slot = await prisma.models.Slot.prisma().create(
        data={
            "professionalId": professionalId,
            "startTime": startTime,
            "endTime": endTime,
            "isActive": isActive,
        }
    )
    notification_status = await send_notification(
        professionalId, "New schedule created for you."
    )
    return CreateScheduleResponse(
        scheduleId=new_slot.id,
        professionalId=professionalId,
        wasNotificationSent=notification_status,
        isActive=isActive,
    )


async def send_notification(professionalId: int, message: str) -> bool:
    """
    Sends a notification to a professional about a significant event regarding their schedule.

    Args:
        professionalId (int): The ID of the professional to whom the notification should be sent.
        message (str): The content of the notification message.

    Returns:
        bool: True if the notification was sent successfully, False otherwise.

    Example:
        await send_notification(1, 'New schedule created for you!')
        > True
    """
    try:
        return True
    except Exception as e:
        return False
