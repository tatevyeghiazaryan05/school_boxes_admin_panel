import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from auth import auth_router
from AdminPanelServices import (admin_panel_product_service,
                                admin_panel_order_service,
                                admin_panel_notification_service,
                                admin_panel_feedback_service)


conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="password",
    database="school_boxes_project",
    cursor_factory=RealDictCursor
    )

cursor = conn.cursor()

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/admin_images", StaticFiles(directory="admin_images"), name="admin_images")


app.include_router(auth_router)
app.include_router(admin_panel_product_service.admin_product_router)
app.include_router(admin_panel_order_service.admin_orders_router)
app.include_router(admin_panel_notification_service.admin_notification_router)
app.include_router(admin_panel_feedback_service.admin_feedback_router)
