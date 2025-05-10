import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from auth import auth_router
from admins import admin_router

from fastapi.staticfiles import StaticFiles


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
app.include_router(admin_router)

#todo image must be url+
#todo add real products+
