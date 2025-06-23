import csv
import os
from typing import List
from config import logger
from parsers.models import ProductDetail


def save_to_csv(products: List[ProductDetail], filename: str = "atb_products.csv") -> None:
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "price", "old_price", "image_url", "date", "tag_shop"])
            for product in products:
                writer.writerow(
                    [product.title,
                     product.price,
                     product.old_price,
                     product.image_url,
                     product.date,
                     product.tag_shop])
        logger.info(f"Дані збережено у файл {filename}")
    except Exception as e:
        logger.error(f"Помилка при збереженні у CSV: {e}")



def load_atb_products_from_csv(filename: str = "atb_products.csv") -> List[ProductDetail]:
    file_path = os.path.join(os.path.dirname(__file__), "..", "parsers", "atb", filename)
    file_path = os.path.abspath(file_path)

    products = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products.append(ProductDetail(
                title=row["title"],
                price=float(row["price"]),
                old_price=float(row["old_price"]) if row.get("old_price") else 0.0,
                image_url=row.get("image_url", ""),
                date=row.get("date", ""),
                tag_shop=row.get("tag_shop", "")
            ))
    return products


def search_in_products(title: str, filename: str = "atb_products.csv") -> list[str]:
    file_path = os.path.join(os.path.dirname(__file__), "..", "parsers", "atb", filename)
    file_path = os.path.abspath(file_path)
    matched = []
    title_lower = title.lower()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if title_lower in row["title"].lower():
                result_line = f"🛒 {row['title']} — {row['price']} ({row['old_price']})"
                matched.append(result_line)

    return matched
