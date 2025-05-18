import main
from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File
from security import pwd_context, create_access_token
import shutil
from schemas import AdminLoginSchema
import os
from datetime import datetime
from fastapi.responses import FileResponse
auth_router = APIRouter(prefix="/adminpanel")


@auth_router.post("/api/admin/auth/sign-up")
def admin_signup(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        file: UploadFile = File(None),
):
    Upload_Dir = "admin_images"
    BASE_URL = "http://localhost:8001"
    if not os.path.exists(Upload_Dir):
        os.makedirs(Upload_Dir)

    main.cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
    if main.cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered.")

    if file and file.filename != "":
        print("hello")
        l = file.filename.split(".")

        image_name = l[0] + " " + str(datetime.now()).replace(":", "") + "." + l[-1]
        file_path = f"{Upload_Dir}/{image_name}"
        image_url=f"{BASE_URL}/{file_path}"

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except PermissionError:
            raise HTTPException(status_code=500, detail="File write error")
    else:
        image_url = f"{BASE_URL}/{Upload_Dir}/default.png"

    hashed_password = pwd_context.hash(password)

    main.cursor.execute("INSERT INTO admins (name, email, password, image_name) VALUES (%s,%s,%s,%s)",
                        (name, email, hashed_password, image_url))
    main.conn.commit()
    return {"message": "Sign Up Successfully!", "image_url": image_url}


@auth_router.post("/api/admin/auth/login")
def admin_login(login_data: AdminLoginSchema):
    email = login_data.email
    password = login_data.password

    main.cursor.execute("SELECT * FROM admins WHERE email = %s",
                        (email,))
    admin = main.cursor.fetchone()
    admin = dict(admin)
    admin_password_db = admin.get("password")

    if not pwd_context.verify(password, admin_password_db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="password is not correct!!"
        )
    else:
        admin_id_db = admin.get("id")
        admin_email_db = admin.get("email")
        return create_access_token({"id": admin_id_db, "email": admin_email_db})

