import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI



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
