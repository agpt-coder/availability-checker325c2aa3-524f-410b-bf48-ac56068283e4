import prisma
import prisma.models
from pydantic import BaseModel


class UpdateNotificationStatusResponse(BaseModel):
    """
    Response model confirming the updated status of the notification. It returns the id and new read status ensuring that the client is aware of the successful update.
    """

    id: int
    read: bool


class Role:
    ADMIN: str = "ADMIN"
    PROFESSIONAL: str = "PROFESSIONAL"
    REGISTERED_USER: str = "REGISTERED_USER"
    GUEST: str = "GUEST"


async def updateNotificationStatus(
    id: int, read: bool, updater_role: Role
) -> UpdateNotificationStatusResponse:
    """
    Updates the status of a specific notification, typically from 'unread' to 'read'. This API is essential for maintaining the relevance and currentness of user interfaces, ensuring that users have an accurate count of new versus reviewed notifications.

    Args:
    id (int): The unique identifier of the notification to be updated.
    read (bool): The updated status of the notification, indicating whether it has been read by the user.
    updater_role (Role): Role of the user updating the notification, to ensure that only allowed roles (Admin, Professional, Registered User) can change the notification status.

    Returns:
    UpdateNotificationStatusResponse: Response model confirming the updated status of the notification. It returns the id and new read status ensuring that the client is aware of the successful update.
    """
    allowed_roles = {Role.ADMIN, Role.PROFESSIONAL, Role.REGISTERED_USER}
    if updater_role not in allowed_roles:
        raise PermissionError(
            "The user's role does not permit updating notification status."
        )
    notification = await prisma.models.Notification.prisma().find_unique(
        where={"id": id}
    )
    if notification is None:
        raise ValueError("Notification not found with the specified ID.")
    updated_notification = await prisma.models.Notification.prisma().update(
        {"where": {"id": id}, "data": {"read": read}}
    )
    return UpdateNotificationStatusResponse(
        id=updated_notification.id, read=updated_notification.read
    )
