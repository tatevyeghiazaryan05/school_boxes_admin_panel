import os
import shutil
from datetime import datetime, timedelta

from pydantic import EmailStr

from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File

import main
from email_service import send_verification_email
from schemas import AdminLoginSchema, AdminPasswordRecover
from security import pwd_context, create_access_token


auth_router = APIRouter(prefix="/adminpanel", tags=["adminauth"])


@auth_router.post("/api/admin/auth/sign-up")
def admin_signup(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        file: UploadFile = File(None),
):
    Upload_Dir = "admin_images"
    BASE_URL = "http://localhost:8001"
    try:
        if not os.path.exists(Upload_Dir):
            os.makedirs(Upload_Dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating upload directory: {str(e)}")

    try:
        main.cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        if main.cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error during email check: {str(e)}")

    try:

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

    except HTTPException:
        raise
    except Exception as e:
        main.conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during sign-up: {str(e)}")


@auth_router.post("/api/admin/auth/login")
def admin_login(login_data: AdminLoginSchema):
    email = login_data.email
    password = login_data.password

    try:
        main.cursor.execute("SELECT * FROM admins WHERE email = %s",
                        (email,))
        admin = main.cursor.fetchone()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@auth_router.put("/api/admin/password/change/code/{email}")
def send_password_change_code_to_email(email: EmailStr):
    try:
        main.cursor.execute("SELECT * FROM admins WHERE email=%s",
                            (email,))
        user = main.cursor.fetchone()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server error"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="not such user!"

        )

    verification_code = send_verification_email(email)
    main.cursor.execute("INSERT INTO changepasswordcodes (code,email) VALUES(%s,%s)",
                        (verification_code, email))

    main.conn.commit()


@auth_router.post("/api/admin/password/recovery/by/email")
def password_recovery(recover_data: AdminPasswordRecover):
    try:
            code = recover_data.code

            new_password = pwd_context.hash(recover_data.new_password)

            try:
                main.cursor.execute("SELECT * FROM changepasswordcodes WHERE code=%s",
                                (code,))
                data = main.cursor.fetchone()

            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="server error"
                )

            if not data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Code is incorrect!"

                )

            data = dict(data)
            created_at = data.get("created_at")
            expiration_time = created_at + timedelta(minutes=15)
            if datetime.now() > expiration_time:
                main.cursor.execute("DELETE FROM changepasswordcodes WHERE code=%s", (code,))
                main.conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Code has expired after 15 minutes."
                )

            main.cursor.execute("UPDATE admins SET password =%s WHERE email=%s",
                                (new_password, data["email"]))

            main.conn.commit()

            main.cursor.execute("DELETE FROM changepasswordcodes WHERE code = %s",
                            (code,))
            main.conn.commit()
            return "Recovered successfully!!"
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Server error during password recovery")

