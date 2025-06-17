import csv
import logging
import time
from dataclasses import astuple
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.base_scraper import BaseScraper
from parsers.models import ProductDetail, PRODUCT_FIELDS


class AtbScraper(BaseScraper):
    def __init__(self, url: str = "https://www.atbmarket.com/catalog/economy", driver: WebDriver = None):
        if driver is None:
            driver = webdriver.Chrome()
        super().__init__(driver, url)

    def _accept_age_verification(self) -> None:
        """Підтвердження віку, якщо з'явиться відповідне вікно"""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "alcohol-modal__submit"))
            )
            button.click()
        except Exception:
            pass

    # def get_num page(self) -> int:
    #     try:
    #         self.driver.get(self.url)
    #         pagination = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.CLASS_NAME, "pagination__item.pagination__item_last"))
    #         ).text
    #         return int(num_pages)


    def get_title(self) -> Optional[str]:
        try:
            self.driver.get(self.url)
            self._accept_age_verification()
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "catalog-item.js-product-container"))
            ).text
            return title
        except Exception as e:
            print(f"Помилка при отриманні title: {str(e)}")
            return None

    def scrape(self) -> List[ProductDetail]:
        """Реалізація абстрактного методу"""
        try:
            self.driver.get(self.url)
            self._accept_age_verification()
            time.sleep(5)

            products = []
            items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "catalog-item.js-product-container"))
            )

            for item in items:
                try:
                    title = item.find_element(By.CLASS_NAME, "catalog-item__title").text
                    price = item.find_element(By.CLASS_NAME, "product-price__top").text
                    products.append(ProductDetail(title=title, price=price))
                except Exception as e:
                    print(f"Помилка при парсингу продукту: {str(e)}")

            return products
        except Exception as e:
            print(f"Помилка при скрапінгу: {str(e)}")
            return []


    def write_product_to_csv(products: [ProductDetail]) -> None:
        """Записує продукт у файл csv"""
        with open("products.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(PRODUCT_FIELDS)
            writer.writerow([astuple(product) for product in products])

def main():
    scraper = AtbScraper()
    products = scraper.scrape()
    print(f"\nВсього зібрано {len(products)} продуктів")
    for product in products:
        print(f"{product.title}: {product.price}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
