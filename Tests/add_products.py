import os

import requests
import json
from icrawler.builtin import BingImageCrawler



# LOGIN_URL = "http://localhost:8001/adminpanel/api/login"
# UPLOAD_URL = "http://localhost:8001/adminpanel/api/product/add"
#
# email = input("Enter your admin email: ").strip()
# password = input("Enter your password: ").strip()
#
# login_data = {
#     "email": email,
#     "password": password
# }
#
# try:
#     login_response = requests.post(LOGIN_URL, json=login_data)
#     login_response.raise_for_status()
# except requests.RequestException as e:
#     raise RuntimeError(f"Login request failed: {e}")
#
# try:
#     token = login_response.json().get("access_token")
# except json.JSONDecodeError:
#     raise RuntimeError("Login response is not valid JSON")
#
#
# if not token:
#     raise RuntimeError("Login successful but token missing from response.")
#
# if not os.path.exists("products.json"):
#     raise FileNotFoundError("'products.json' file not found.")
#
#
# try:
#     with open("products.json", "r", encoding="utf-8") as f:
#         products = json.load(f)
# except json.JSONDecodeError:
#     raise RuntimeError("Invalid JSON format in 'products.json'.")

#
# headers = {
#     "Authorization": f"Bearer {token}"
# }
#
#

# def downloa_product_image(tags: list, brand_name: str, download_path: str):
#     query = f"{brand_name} " + " ".join(tags)
#     folder = os.path.dirname(download_path)
#     filename = os.path.basename(download_path)
#
#     # Ensure folder exists
#     os.makedirs(folder, exist_ok=True)

    # Use Bing image crawler
    # crawler = BingImageCrawler(storage={'root_dir': folder})
    # crawler.crawl(keyword=query, max_num=1)

    # Rename the first downloaded file to match desired output
    # downloaded_files = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
    # if downloaded_files:
    #     os.rename(os.path.join(folder, downloaded_files[0]), download_path)
    #     print(f"Image downloaded and saved to {download_path}")
    # else:
    #     print("No image downloaded.")


# for product in products:
#     download_product_image(
#     tags=product["tags"],
#     brand_name=product["product_brand"],
#     download_path=product["image_path"]
# )



# for product in products:
#     data = {
#         "product_brand": product["product_brand"],
#         "category": product["category"],
#         "color": product["color"],
#         "price": product["price"],
#         "count": product["count"],
#         "description": product["description"],
#         "is_active": product["is_active"],
#         "discount": product["discount"],
#         "tags": product["tags"]
#     }
#
#     image_path = product.get("image_path")
#     if not image_path or not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image file not found for product '{product['product_brand']}': {image_path}")
#
#     with open(image_path, "rb") as img_file:
#         files = {"file": img_file}
#         try:
#             response = requests.post(UPLOAD_URL, headers=headers, data=data, files=files)
#             response.raise_for_status()
#         except requests.RequestException:
#             try:
#                 response = requests.post(UPLOAD_URL, headers=headers, data=data, files=files)
#                 response.raise_for_status()
#             except requests.RequestException as e:
#                 raise RuntimeError(f"Failed to upload '{product['product_brand']}': {e}")


import os
import json
import requests
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler

PRODUCTS_JSON = "products.json"
PRODUCT_IMAGES_FOLDER = "product_images"
UPLOAD_URL = "http://localhost:8001/adminpanel/api/product/add" # replace with your real URL
HEADERS = {"Authorization": "Bearer your_admin_token"}  # update this


def download_product_image(tags: list, brand_name: str) -> str:
    query = f"{brand_name} " + " ".join(tags)
    filename = f"{brand_name}_{'_'.join(tags)}.jpg".replace(" ", "_")
    folder = PRODUCT_IMAGES_FOLDER
    os.makedirs(folder, exist_ok=True)
    download_path = os.path.join(folder, filename)

    def try_crawler(crawler_class, label):
        print(f"Trying {label} image search for: {query}")
        crawler = crawler_class(storage={'root_dir': folder})
        crawler.crawl(keyword=query, max_num=1)

        downloaded_files = sorted(
            os.listdir(folder),
            key=lambda x: os.path.getctime(os.path.join(folder, x))
        )
        for file in downloaded_files:
            if file.endswith((".jpg", ".jpeg", ".png", ".webp")) and file != filename:
                return file
        return None

    image_file = try_crawler(BingImageCrawler, "Bing")
    if not image_file:
        image_file = try_crawler(GoogleImageCrawler, "Google")
    if not image_file:
        print("No image found. Using placeholder.")
        placeholder_url = "https://via.placeholder.com/300?text=No+Image"
        response = requests.get(placeholder_url)
        with open(download_path, 'wb') as f:
            f.write(response.content)
        return download_path

    os.rename(os.path.join(folder, image_file), download_path)
    print(f"Image saved to {download_path}")
    return download_path


# Load products from JSON
with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
    products = json.load(f)

# Process each product
for product in products:
    if not product.get("image_path") or not os.path.exists(product["image_path"]):
        image_path = download_product_image(product["tags"], product["product_brand"])
        product["image_path"] = image_path

    data = {
        "product_brand": product["product_brand"],
        "category": product["category"],
        "color": product["color"],
        "price": product["price"],
        "count": product["count"],
        "description": product["description"],
        "is_active": product["is_active"],
        "discount": product["discount"],
        "tags": product["tags"]
    }

    try:
        with open(product["image_path"], "rb") as img_file:
            files = {"file": img_file}
            response = requests.post(UPLOAD_URL, headers=HEADERS, data=data, files=files)
            response.raise_for_status()
            print(f"✅ Uploaded: {product['product_brand']}")
    except Exception as e:
        print(f"❌ Failed to upload {product['product_brand']}: {e}")

# Save updated image paths back to products.json (optional)
with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)
    print("✅ Updated products.json with image paths.")

# todo
