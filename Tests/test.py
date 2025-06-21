def download_product_image(tags: list, brand_name: str, download_path: str):
    query = f"{brand_name} " + " ".join(tags)
    folder = os.path.dirname(download_path)
    filename = os.path.basename(download_path)

    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    # Use Bing image crawler
    crawler = BingImageCrawler(storage={'root_dir': folder})
    crawler.crawl(keyword=query, max_num=1)

    # Rename the first downloaded file to match desired output
    downloaded_files = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
    if downloaded_files:
        os.rename(os.path.join(folder, downloaded_files[0]), download_path)
        print(f"Image downloaded and saved to {download_path}")
    else:
        print("No image downloaded.")



download_product_image(
    tags=["highlighter", "yellow"],
    brand_name="Skarlet",
    download_path="./product_images/skarlet_highlighter_y.jpg"
)
