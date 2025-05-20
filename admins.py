import os

import main
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from schemas import ProductNameChangeSchema, ProductKindChangeSchema, ProductPriceChangeSchema, ProductCategoryChangeSchema, AdminPasswordRecover
from security import get_current_admin, pwd_context
from fastapi.responses import FileResponse
from datetime import datetime,  date, timedelta
import shutil
from pydantic import EmailStr
from email_service import send_verification_email


admin_router = APIRouter(prefix="/adminpanel")


@admin_router.post("/api/product/add")
def product_add(
        product_brand: str = Form(...),
        category: str = Form(...),
        color: str = Form(...),
        price: float = Form(...),
        count: int = Form(...),
        description: str = Form(...),
        is_active: bool = Form(True),
        discount: float = Form(0.0),
        tags: str = Form(""),
        file: UploadFile = File(None),
        token=Depends(get_current_admin)
):
    upload_dir = "uploads"
    BASE_URL = "http://localhost:8000"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    if file:
        l = file.filename.split(".")

        image_filename = l[0] + "_" + str(datetime.now()).replace(":", "").replace(" ", "_") + "." + l[-1]
        file_path = f"{upload_dir}/{image_filename}"
        image_url = f"{BASE_URL}/uploads/{image_filename}"

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except PermissionError:
            raise HTTPException(status_code=500, detail="File write error")

    else:
        image_url = f"{BASE_URL}/uploads/products.jpg"

    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    main.cursor.execute(
        """INSERT INTO products (product_brand, category, color, price, count,
                description, is_active, image_url,
                discount, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ( product_brand, category, color, price, count,
            description, is_active, image_url,
            discount, tags_list)
    )
    main.conn.commit()

    return {"message": "Product  added successfully", "image_url": image_url}


@admin_router.delete("/api/products/delete/by-id/{product_id}")
def delete_product(product_id: int, token=Depends(get_current_admin)):
    main.cursor.execute("SELECT * FROM products WHERE id = %s",
                        (product_id,))
    product = main.cursor.fetchone()
    product = dict(product)
    image_url = product.get("image_url")
    image_name = os.path.basename(image_url)
    main.cursor.execute("DELETE FROM products WHERE id = %s",
                        (product_id,))
    main.conn.commit()

    if image_name == "products.jpg":
        return "Product deleted (default image not removed)"

    file_path = f"product_images/{image_name}"
    print(f"file_path:{file_path}")

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")


@admin_router.put("/api/products/change/product_name/by/product_id/{product_id}")
def change_products(product_id: int, change_data: ProductNameChangeSchema, token=Depends(get_current_admin)):
    main.cursor.execute("UPDATE products SET name = %s WHERE id = %s", (change_data.name, product_id))
    main.conn.commit()
    return "Product name updated successfully!!"


@admin_router.put("/api/products/change/product_kind/by/product_id/{product_id}")
def change_products(product_id: int, change_data: ProductKindChangeSchema, token=Depends(get_current_admin)):
    main.cursor.execute("UPDATE products SET kind = %s WHERE id = %s", (change_data.kind, product_id))
    main.conn.commit()
    return "Product kind updated successfully!!"


@admin_router.put("/api/products/change/product_price/by/product_id/{product_id}")
def change_products(product_id: int, change_data: ProductPriceChangeSchema, token=Depends(get_current_admin)):
    main.cursor.execute("UPDATE products SET price = %s WHERE id = %s", (change_data.price, product_id))
    main.conn.commit()
    return "Product price updated successfully!!"


@admin_router.put("/api/products/change/product_category/by/product_id/{product_id}")
def change_products(product_id: int, change_data: ProductCategoryChangeSchema, token=Depends(get_current_admin)):
    main.cursor.execute("UPDATE products SET category = %s WHERE id = %s", (change_data.category, product_id))
    main.conn.commit()
    return "Product category updated successfully!!"


@admin_router.put("/api/products/change/product_image/by/product_id/{product_id}")
def change_products(product_id: int, file: UploadFile = File(...), token=Depends(get_current_admin)):

    if file:
        upload_dir = "product_images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        image_url = f"http://127.0.0.1:8000/api/images/get_image/{file.filename}"

        main.cursor.execute("UPDATE products SET image = %s WHERE id = %s", (image_url, product_id))
        main.conn.commit()
        return "Product image updated successfully!!"


@admin_router.get("/api/products/get/image/by/id/{product_id}")
def get_images(product_id: int):
    main.cursor.execute("SELECT image FROM products WHERE id=%s",
                        (product_id,))
    result = main.cursor.fetchone()
    if result is None:
        return "Product not found "

    image_name = result['image']
    image_path = os.path.join("product_images", image_name)

    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )

    return FileResponse(path=image_path, media_type="image/jpeg", filename=image_name)


@admin_router.get("/admins/api/get/feedback/{start_date}/{end_date}", status_code=200)
def get_feedback(start_date: date, end_date: date):
    main.cursor.execute("SELECT * FROM feedback WHERE created_at >= %s AND created_at <= %s",
                        (start_date, end_date))
    feedbacks = main.cursor.fetchall()
    return feedbacks


@admin_router.put("/api/admin/password/change/code/{email}")
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


@admin_router.post("/api/admin/password/recovery/by/email")
def password_recovery(recover_data: AdminPasswordRecover):
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


@admin_router.get("/api/admin/get/orders/by/id/{order_id}")
def get_order_by_id(order_id: int):
    main.cursor.execute("SELECT * FROM orders WHERE id=%s",
                        (order_id,))
    order = main.cursor.fetchone()
    return order


@admin_router.get("/api/admin/get/orders/by/date/{start_date}/{end_date}")
def get_order_by_date(start_date: date, end_date: date):
    main.cursor.execute("SELECT * FROM orders WHERE created_at >= %s AND created_at <= %s",
                        (start_date, end_date))
    orders = main.cursor.fetchall()
    return orders


@admin_router.get("/api/admin/get/orders/by/price/{min_price}/{max_price}")
def get_order_by_date(min_price: float, max_price: float):
    main.cursor.execute("SELECT * FROM orders WHERE total_price >= %s AND total_price <= %s",
                        (min_price, max_price))
    orders = main.cursor.fetchall()
    return orders


@admin_router.get("/api/admin/notifications")
def get_admin_notifications():
    main.cursor.execute("SELECT id, message, created_at FROM notifications WHERE is_read = %s",
                        (False, ))
    return main.cursor.fetchall()


@admin_router.post("/api/admin/notifications/mark-read/{notification_id}")
def mark_notification_as_read(notification_id: int):
    main.cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s",
                        (notification_id,))
    main.conn.commit()
    return {"message": "Notification marked as read"}


@admin_router.delete("/api/admin/notifications/delete/by/id/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, token=Depends(get_current_admin)):
    try:
        main.cursor.execute("DELETE FROM notifications WHERE id=%s",
                        (notification_id,))

        main.conn.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
