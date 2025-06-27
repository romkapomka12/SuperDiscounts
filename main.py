import asyncio
import os
import logging
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
# from bot.handlers import router as show_products
from config import logger
from config.config import DB_FILE_PATH
from data.db_manager import load_all_products_from_db, init_db
from bot import handlers

load_dotenv()

PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT_DIR)

API_TOKEN = os.environ["API_TOKEN"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    logger.info("Запуск бота...")

    # КРОК 1: Ініціалізуємо базу даних. Гарантуємо, що таблиця існує.
    logger.info("Ініціалізація бази даних...")
    init_db()

    # КРОК 2: Завантажуємо дані з БД.
    logger.info("Завантаження даних про товари...")
    products_from_db = load_all_products_from_db()

    # КРОК 3: Заповнюємо глобальні змінні в модулі handlers.
    # Тепер хендлери будуть працювати з актуальними даними.
    handlers.ALL_PRODUCTS_LIST = products_from_db
    handlers.PRODUCTS_BY_ID = {p['id']: p for p in products_from_db}

    logger.info(f"✅ Успішно завантажено {len(handlers.ALL_PRODUCTS_LIST)} товарів.")

    # КРОК 4: Включаємо роутер і запускаємо бота.
    dp.include_router(handlers.router)
    logger.info("Бот готовий до роботи. Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")