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
from urllib3.filepost import writer

from parsers.base_scraper import BaseScraper
from parsers.models import ProductDetail, PRODUCT_FIELDS


class AtbScraper(BaseScraper):
    def __init__(self, url: str = "https://www.atbmarket.com/catalog/economy", driver: WebDriver = None):
        if driver is None:
            driver = webdriver.Chrome()
        super().__init__(driver, url)

    def _manual_cloudflare_check(self) -> None:
        """Чекає на ручне проходження Cloudflare"""
        logging.info("Очікування ручного проходження Cloudflare...")
        input("Будь ласка, пройдіть перевірку Cloudflare вручну у відкритому браузері, потім натисніть Enter тут...")

        WebDriverWait(self.driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "catalog-item")))

        logging.info("Cloudflare пройдено успішно")

    def _accept_age_verification(self) -> None:
        """Підтвердження віку, якщо з'явиться відповідне вікно"""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "alcohol-modal__submit"))
            )
            button.click()
        except Exception:
            pass

    def get_num_page(self) -> int:
        self.driver.get(self.url)
        max_page = 1
        try:
            while True:
                more_button = (WebDriverWait(self.driver, 10).
                               until(EC.presence_of_element_located((By.CLASS_NAME, "product-pagination"))))
                current_page = int(more_button.get_attribute("data-page"))
                if current_page > max_page:
                    max_page = current_page

                more_button.click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, f"button.product-pagination__more[data-page='{current_page + 1}']"))
                )
        except Exception as e:
            logging.error(f"Загальна кількість сторінок: {max_page}")
            return max_page
        except Exception as e:
            logging.error(f"Не вдалося визначити кількість сторінок: {e}")


    def parse_all_pages(self) -> List[ProductDetail]:
        all_products = []
        try:
            total_page = self.get_num_page()

            for page in range(1, total_page + 1):
                page_url = f"{self.url}?page={page}"
                self.driver.get(page_url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "catalog-item"))
                )

                products = self.scrape()
                all_products.extend(products)
                self.write_products_to_csv(products)

                logging.info(f"Парсинг на сторінці {page} завершено. Знайдено {len(products)}")
        except Exception as e:
            logging.error(f"Помилка парсингу : {e}")
        finally:
            self.driver.quit()
        return all_products


    def scrape(self) -> List[ProductDetail]:
        products = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "catalog-item.js-product-container"))
            )
            items = self.driver.find_elements(By.CLASS_NAME, "catalog-item.js-product-container")
            for item in items:
                try:
                    title = item.find_element(By.CLASS_NAME, "catalog-item__title").text
                    price = item.find_element(By.CLASS_NAME, "product-price__top").get_attribute("value")
                    old_price = item.find_element(By.CLASS_NAME, "product-price__bottom").get_attribute("value")
                    date = item.find_element(By.CLASS_NAME, "custom-product-label__date").text
                    logging.info(f"Знайдено товар: {title} - {price} - {old_price} -{date}")

                    products.append(ProductDetail(title=title, price=price, old_price=old_price, date=date))
                except Exception as e:
                    logging.error(f"Помилка при парсингу продукту: {str(e)}")
                    logging.error(f"HTML елемента: {item.get_attribute('innerHTML')}")

            return products
        except Exception as e:
            print(f"Помилка при скрапінгу: {str(e)}")
            return []

    @staticmethod
    def write_product_to_csv(products: [ProductDetail], filename: str = "atb_products.csv") -> None:
        """Записує продукт у файл csv"""
        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                if file.tell() == 0:
                    writer.writerow(PRODUCT_FIELDS)
                    writer.writerow(astuple(product) for product in products)
        except Exception as e:
            logging.error(f"Помилка при записі до CSV: {e}")




def main():
    try:
        scraper = AtbScraper()
        products = scraper.parse_all_pages()

        logging.info(f"\nЗавершено! Всього зібрано {len(products)} продуктів")
        logging.info(f"Дані збережено у файлі 'atb_products.csv'")

        for product in products:
            print(f"{product.title}: {product.price}")

    except Exception as e:
        logging.error(f"Критична помилка: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
