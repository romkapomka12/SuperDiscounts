import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers import router
from parsers import atb

load_dotenv()

API_TOKEN = os.environ["API_TOKEN"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    atb()
    # logging.basicConfig(level=logging.INFO)
    # try:
    #     asyncio.run(main())
    # except KeyboardInterrupt:
    #     print("exit")