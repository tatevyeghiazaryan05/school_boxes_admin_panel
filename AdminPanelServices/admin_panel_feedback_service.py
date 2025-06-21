from datetime import date

from fastapi import APIRouter, Depends, HTTPException

import main
from security import get_current_admin


admin_feedback_router = APIRouter(prefix="/adminpanel", tags=["admin_feedback_service"])


@admin_feedback_router.get("/admins/api/get/feedback/{start_date}/{end_date}", status_code=200)
def get_feedback(start_date: date, end_date: date, token=Depends(get_current_admin)):
    try:
        main.cursor.execute("SELECT * FROM feedback WHERE created_at >= %s AND created_at <= %s",
                        (start_date, end_date))
        feedbacks = main.cursor.fetchall()
        return feedbacks
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while fetching feedback")
