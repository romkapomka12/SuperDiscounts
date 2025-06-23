import time
from typing import List, Optional
from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import logger, setup_undetected_driver
from config.logger import setup_logging
from data.save_product import save_to_csv
from parsers.models import ProductDetail


# @dataclass
# class ProductDetail:
#     title: str
#     price: str
#     old_price: Optional[str] = None
#     image_url: Optional[str] = None
#     date: Optional[str] = None



class ATBParser:
    def __init__(self, driver: WebDriver = None):
        self.driver = driver if driver else setup_undetected_driver()
        self.base_url = "https://www.atbmarket.com/catalog/economy"
        self.tag_shop = "АТБ-Маркет"

    def _accept_age_verification(self) -> None:
        """Підтвердження віку, якщо з'явиться відповідне вікно"""
        try:
            # Чекаємо до 10 секунд на появу вікового обмеження
            button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".alcohol-modal__submit"))
            )
            # Клікаємо за допомогою JavaScript (надійніше)
            self.driver.execute_script("arguments[0].click();", button)
            logger.info("Вікове обмеження підтверджено")
            time.sleep(2)  # Важлива пауза після кліку
        except Exception as e:
            logger.debug(f"Вікове обмеження не знайдено: {e}")

    def _handle_notification(self) -> None:
        try:
            # Чекаємо і закриваємо сповіщення
            WebDriverWait(self.driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='Оповищення']")))
            decline_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Отклонить']")))
            decline_btn.click()
            self.driver.switch_to.default_content()
            logger.info("Запит на сповіщення відхилено")
        except Exception as e:
            logger.debug(f"Запит на сповіщення не знайдено: {e}")

    def _solve_cloudflare(self):
        """Автоматичний обхід Cloudflare"""
        try:
            # Очікування перевірки Cloudflare
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "challenge-form")))

            # Спробуємо автоматично вирішити капчу
            try:
                self.driver.find_element(By.XPATH,
                                         "//input[@type='checkbox']").click()
                time.sleep(2)
            except:
                pass

            # Очікуємо завершення перевірки
            WebDriverWait(self.driver, 60).until_not(
                EC.presence_of_element_located((By.ID, "challenge-form")))

            return True
        except Exception as e:
            print(f"Не вдалося автоматично обійти Cloudflare: {e}")
            return False

    def _get_total_pages(self) -> int:
        """Визначає загальну кількість сторінок"""
        try:
            self.driver.get(self.base_url)

            # 1. Спочатку обробляємо вікове обмеження
            self._accept_age_verification()

            # 2. Чекаємо на завантаження пагінації
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-pagination"))
            )

            max_page = 1
            while True:
                try:
                    # Знаходимо кнопку "Показати ще"
                    more_button = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.product-pagination__more"))
                    )

                    # Отримуємо поточну сторінку
                    current_page = int(more_button.get_attribute("data-page"))
                    if current_page > max_page:
                        max_page = current_page + 1

                    # Клікаємо за допомогою JS
                    self.driver.execute_script("arguments[0].click();", more_button)
                    logger.info(f"Клікнуто 'Показати ще' для сторінки {current_page}")
                    time.sleep(6)

                    # Чекаємо оновлення кнопки
                    WebDriverWait(self.driver, 10).until(
                        lambda d: not d.find_elements(By.CSS_SELECTOR, "button.product-pagination__more") or
                                  d.find_elements(By.CSS_SELECTOR,
                                                  f"button.product-pagination__more[data-page='{current_page + 1}']")
                    )
                    # time.sleep(6)  # Пауза між кліками

                except Exception as e:
                    logger.info(f"Остання сторінка: {max_page}")
                    break

            return max_page

        except Exception as e:
            logger.error(f"Помилка при визначенні кількості сторінок: {e}")
            return 1

    def _parse_page(self) -> List[ProductDetail]:
        """Парсить товари з поточної сторінки"""
        try:
            if not self._solve_cloudflare:
                self.driver.get(self.base_url)
                raise Exception("Не вдалося пройти Cloudflare")

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog-item.js-product-container")))

            products = []
            items = self.driver.find_elements(By.CSS_SELECTOR, ".catalog-item.js-product-container")

            for item in items:
                try:
                    title = item.find_element(
                        By.XPATH, ".//div[contains(@class, 'catalog-item__title')]/a"
                    ).text.strip()
                    price = item.find_element(By.CSS_SELECTOR, ".product-price__top").get_attribute("value")
                    old_price = item.find_element(By.CSS_SELECTOR, ".product-price__bottom").get_attribute("value")
                    image_url = item.find_element(By.CSS_SELECTOR, "img.catalog-item__img"
                ).get_attribute("src")
                    date = item.find_element(By.CSS_SELECTOR, ".custom-product-label__date").text.strip()
                    tag_shop =  self.tag_shop

                    products.append(
                        ProductDetail(
                            title=title,
                            price=price,
                            old_price=old_price,
                            image_url=image_url,
                            date=date,
                            tag_shop=tag_shop))
                    logger.debug(f"Додано товар: {title}")

                except Exception as e:
                    logger.warning(f"Помилка парсингу товару: {e}")
                    return []

        except Exception as e:
            logger.error(f"Критична помилка при парсингу сторінки: {e}")
            return []
        return products

    def parse_all_pages(self) -> List[ProductDetail]:
        """Парсить всі сторінки з товарами"""
        all_products = []
        try:
            self._accept_age_verification()
            total_pages = self._get_total_pages()

            for page in range(1, total_pages + 1):
                page_url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
                self.driver.get(page_url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog-item.js-product-container")))

                products = self._parse_page()
                all_products.extend(products)
                logger.info(f"Сторінка {page}/{total_pages}: знайдено {len(products)} товарів")
                time.sleep(1)

        except Exception as e:
            logger.error(f"Помилка при парсингу: {e}")
        finally:
            self.driver.quit()

        return all_products




def main():
    logger.info("Запуск парсингу АТБ")
    parser = ATBParser()
    products = parser.parse_all_pages()
    save_to_csv(products)
    logger.info(f"Парсинг завершено. Знайдено {len(products)} товарів")


if __name__ == "__main__":
    setup_logging()
    main()

