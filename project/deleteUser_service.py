import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponseModel(BaseModel):
    """
    Response model for the delete user operation. It indicates whether the deletion was successful and provides an appropriate message.
    """

    success: bool
    message: str


async def deleteUser(userId: int) -> DeleteUserResponseModel:
    """
    Deletes a user account by their userId. This endpoint will permit deletion by the account owner or by an admin. It requires authentication and provides confirmation upon successful deletion or details on why deletion was not allowed.

    Args:
        userId (int): The unique identifier of the user to be deleted.

    Returns:
        DeleteUserResponseModel: Response model for the delete user operation. It indicates whether the deletion was successful and provides an appropriate message.
    """
    try:
        user = await prisma.models.User.prisma().find_unique(
            where={"id": userId}, include={"notifications": True, "bookings": True}
        )
        if user is None:
            return DeleteUserResponseModel(
                success=False, message="prisma.models.User not found."
            )
        await prisma.models.Booking.prisma().delete_many(where={"userId": userId})
        await prisma.models.Notification.prisma().delete_many(where={"userId": userId})
        await prisma.models.User.prisma().delete(where={"id": userId})
        return DeleteUserResponseModel(
            success=True, message="prisma.models.User successfully deleted."
        )
    except Exception as e:
        return DeleteUserResponseModel(success=False, message=str(e))
