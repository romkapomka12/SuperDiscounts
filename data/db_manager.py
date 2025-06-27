import sqlite3
from typing import List, Dict
from parsers.models import ProductDetail
from config import logger
from config.config import DB_FILE_PATH

DB_FILE = "products.db"


def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        old_price REAL,
        date TEXT,
        image_url TEXT,
        tag_shop TEXT NOT NULL,
        normalized_title TEXT )
                   """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_normalized_title ON products (normalized_title)")
    conn.commit()
    conn.close()
    logger.info("Базу даних ініціалізовано.")


def normalize_title(title: str) -> str:
    """Нормалізація"""
    return ' '.join(title.lower().replace(',', '').replace('"', '').split())


def save_products_to_db(products: List[ProductDetail]):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    # Очищуємо таблицю перед новим записом, щоб не було дублікатів
    cursor.execute("DELETE FROM products")

    for product in products:
        cursor.execute("""
                       INSERT INTO products (id, title, price, old_price, date, image_url, tag_shop, normalized_title)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO
                       UPDATE SET
                           title=excluded.title,
                           price=excluded.price,
                           old_price=excluded.old_price,
                           date =excluded.date,
                           tag_shop=excluded.tag_shop
                       """, (
                           product.id,
                           product.title,
                           product.price,
                           product.old_price,
                           product.date,
                           product.image_url,
                           product.tag_shop,
                           normalize_title(product.title)
                       ))

    conn.commit()
    conn.close()
    logger.info(f"Збережено/оновлено {len(products)} товарів у {DB_FILE}")

def load_all_products_from_db() -> List[Dict]:
    """Завантажуєм всі товари"""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    logger.info(f"Завантажено {len(products)} товарів з бази даних.")
    return products


def search_products_in_db(query: str) -> List[Dict]:
    conn = sqlite3.connect(DB_FILE_PATH)

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_term = f"%{normalize_title(query)}%"
    cursor.execute("SELECT * FROM products WHERE normalized_title LIKE ?", (search_term,))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results
