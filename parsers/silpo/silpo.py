import hashlib
import os
import time
from random import randint
from typing import List, Optional
from dataclasses import dataclass

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import logger, setup_undetected_driver
from config.logger import setup_logging
from data.db_manager import save_products_to_db, init_db
from parsers.models import ProductDetail
import sys
import os
import time


PROJECT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT_DIR)


class SilpoParser:
    def __init__(self, driver: WebDriver = None):
        self.driver = driver if driver else setup_undetected_driver()
        self.base_url = "https://silpo.ua/offers"
        self.tag_shop = "Сільпо"

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
            WebDriverWait(self.driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='Оповищення']")))
            decline_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Отклонить']")))
            decline_btn.click()
            self.driver.switch_to.default_content()
            logger.info("Запит на сповіщення відхилено")
        except Exception as e:
            logger.debug(f"Запит на сповіщення не знайдено: {e}")

    # def _solve_cloudflare(self):
    #     try:
    #         WebDriverWait(self.driver, 30).until(
    #             EC.presence_of_element_located((By.ID, "challenge-form")))
    #
    #         try:
    #             self.driver.find_element(By.XPATH,
    #                                      "//input[@type='checkbox']").click()
    #             time.sleep(2)
    #         except:
    #             WebDriverWait(self.driver, 60).until_not(
    #             EC.presence_of_element_located((By.ID, "challenge-form")))
    #
    #         return True
    #     except Exception as e:
    #         print(f"Не вдалося автоматично обійти Cloudflare: {e}")
    #         return False

    def _handle_cookie_banner(self) -> None:

        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Добре')]]"))
            )
            cookie_button.click()

            logger.info("Згоду на використання cookie прийнято.")
            time.sleep(3)
        except Exception:
            logger.debug("Вікно cookie не знайдено.")


    def _get_total_pages(self) -> int:

        try:
            self.driver.get(self.base_url)
            print(f"Завантажено сторінку: {self.base_url}")

            self._accept_age_verification()
            self._handle_notification()

            pagination_container = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "pagination"))
            )

            last_page_element = pagination_container.find_element(
                By.XPATH, ".//div[contains(@class, 'pagination__items')]/a[last()]"
            )

            last_page_number_str = last_page_element.text.strip()

            print(f"Знайдено текст останньої сторінки: '{last_page_number_str}'")
            print(f"Текст останньої сторінки: '{last_page_number_str}'")
            return int(last_page_number_str)

        except (NoSuchElementException, TimeoutException):

            print("Пагінацію не знайдено")
            return 1

        except Exception as e:

            print(f"Не вдалося визначити кількість сторінок: {e}")
            return 1


    def _parse_page(self) -> List[ProductDetail]:
        try:
            self.driver.get(self.base_url)
            # raise Exception("Не вдалося пройти Cloudflare")

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog__products")))

            products_on_page = []
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.products-list__item")

            for item in items:
                try:
                    title_element = item.find_element(By.CSS_SELECTOR, "div.product-card__title")
                    title = title_element.text.strip()
                    # product_url_element = item.find_element(By.CSS_SELECTOR, "a.product-card")
                    # product_url =product_url_element.get_attribute("href")

                    # if not product_url:
                    #     logger.warning(f"Пропущено елемент без URL-адреси товару.")
                    #     continue

                    image_element = item.find_element(By.CSS_SELECTOR, "img.product-card__product-img")

                    image_url = None
                    try:
                        # image_element = item.find_element(By.CSS_SELECTOR, "img.product-card__img")
                        image_url = image_element.get_attribute("src")
                        if not image_url:
                            # Якщо src пустий, пробуємо data-src (для lazy loading)
                            image_url = image_element.get_attribute("data-src")
                    except NoSuchElementException:
                        logger.warning(f"Не знайдено зображення для товару: {title}")



                    product_id = hashlib.md5(image_url.encode('utf-8')).hexdigest()[:16]

                    price_element = item.find_element(By.CSS_SELECTOR, "div.product-card-price__displayPrice")
                    price = price_element.text.replace('\n', '').strip()

                    old_price = None
                    try:
                        old_price_element = (
                                item.find_element(By.CSS_SELECTOR, "div.product-card-price__old")
                                or item.find_element(By.CSS_SELECTOR, "div.product-card-price__displayOldPrice")
                        )
                        old_price = float(old_price_element.text.strip())
                    except NoSuchElementException:
                        pass

                    if not title or not price:
                        print(f"Пропущено товар без назви або ціни.")
                        continue

                    product = ProductDetail(
                        id=product_id,
                        title=title,
                        price=price,
                        old_price=old_price,
                        image_url=image_url,
                        date=None,
                        tag_shop=self.tag_shop,
                    )

                    products_on_page.append(product)



                except Exception as e:
                    logger.warning(f"Помилка парсингу товару: {e}")
                    continue

        except Exception as e:
            logger.error(f"Критична помилка при парсингу сторінки: {e}")
            return []
        return products_on_page

    def parse_all_pages(self) -> List[ProductDetail]:
        all_products = []
        try:
            total_pages = self._get_total_pages()
            logger.info(f"Загальна кількість сторінок для парсингу: {total_pages}")

            for page in range(1, total_pages + 1):
                page_url = f"{self.base_url}?page={page}"
                logger.info(f"--- Парсинг сторінки {page}/{total_pages}: {page_url} ---")
                self.driver.get(page_url)

                products_from_page = self._parse_page()

                if products_from_page:
                    all_products.extend(products_from_page)
                    logger.info(f"Додано {len(products_from_page)} товарів. Всього зібрано: {len(all_products)}")
                else:
                    logger.warning(f"Не вдалося зібрати товари зі сторінки {page}.")

                time.sleep(1)

        except Exception as e:
            logger.error(f"Помилка при парсингу: {e}")
        finally:
            self.driver.quit()

        return all_products


def main():
    logger.info("Запуск парсингу Сільпо")
    init_db()

    parser = SilpoParser()
    products = parser.parse_all_pages()

    save_products_to_db(products)
    logger.info(f"Парсинг завершено. Знайдено {len(products)} товарів")


if __name__ == "__main__":
    setup_logging()
    main()

















# async def parse_atb_promotions():
#     url = "https://silpo.ua/category/spetsialni-propozytsii-5189"
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             html = await response.text()
#
#     soup = BeautifulSoup(html, 'lxml')
#     promotions = []
#
#     # Тут логіка парсингу конкретних елементів
#     for item in soup.select('.promotion-item'):
#         name = item.select_one('.promo-title').text.strip()
#         price = item.select_one('.promo-price').text.strip()
#         promotions.append({'name': name, 'price': price, 'store': 'ATB'})
#
#     return promotions