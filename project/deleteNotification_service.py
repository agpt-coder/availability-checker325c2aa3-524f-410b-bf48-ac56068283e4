import prisma
import prisma.models
from pydantic import BaseModel


class DeleteNotificationResponse(BaseModel):
    """
    A simple response model for the delete operation. It handles and reflects the deletion status.
    """

    success: bool
    message: str


async def deleteNotification(id: int) -> DeleteNotificationResponse:
    """
    Deletes a specific notification. This route is available for users to manage their notification clutter, removing older or irrelevant notifications from their view.

    Args:
    id (int): The unique identifier of the notification to be deleted.

    Returns:
    DeleteNotificationResponse: A simple response model for the delete operation. It handles and reflects the deletion status.
    """
    notification = await prisma.models.Notification.prisma().find_unique(
        where={"id": id}
    )
    if notification:
        await prisma.models.Notification.prisma().delete(where={"id": id})
        return DeleteNotificationResponse(
            success=True, message="Notification deleted successfully."
        )
    else:
        return DeleteNotificationResponse(
            success=False, message="Notification not found."
        )
