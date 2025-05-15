import os

import main
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from schemas import ProductNameChangeSchema, ProductKindChangeSchema, ProductPriceChangeSchema, ProductCategoryChangeSchema
from security import get_current_admin
from fastapi.responses import FileResponse
from datetime import datetime,  date
import shutil
from pydantic import EmailStr
from email_service import send_verification_email


admin_router = APIRouter()


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
