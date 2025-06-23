import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
# from bot.handlers import router as show_products
from config import logger
from data.save_product import load_atb_products_from_csv
load_dotenv()

API_TOKEN = os.environ["API_TOKEN"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
products = load_atb_products_from_csv()

async def main():
    from bot.handlers import router as show_products
    dp.include_routers(show_products)
    print(f"✅ Завантажено товарів: {len(products)}")
    print("Обробляється callback shop-atb")
    print("🔍 Тип першого продукту:", type(products[0]))
    print("📦 Перший товар:", products[0])
    await dp.start_polling(bot)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")