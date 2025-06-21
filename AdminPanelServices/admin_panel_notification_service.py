from fastapi import APIRouter, Depends, HTTPException, status

import main
from security import get_current_admin


admin_notification_router = APIRouter(prefix="/adminpanel", tags=["admin_notification_service"])


@admin_notification_router.get("/api/admin/notifications")
def get_admin_notifications(token=Depends(get_current_admin)):
    try:
        main.cursor.execute("SELECT id, message, created_at FROM notifications WHERE is_read = %s",
                        (False, ))
        return main.cursor.fetchall()
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while fetching notifications")


@admin_notification_router.put("/api/admin/notifications/mark-read/{notification_id}")
def mark_notification_as_read(notification_id: int, token=Depends(get_current_admin)):
    try:
        main.cursor.execute("UPDATE notifications SET is_read = true WHERE id = %s",
                            (notification_id,))
        main.conn.commit()
        return {"message": "Notification marked as read"}
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while marking notification as read")


@admin_notification_router.delete("/api/admin/notifications/delete/by/id/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, token=Depends(get_current_admin)):
    try:
        main.cursor.execute("DELETE FROM notifications WHERE id=%s",
                        (notification_id,))

        main.conn.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
