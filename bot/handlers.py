import asyncio
import os
import re
from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import bot.keyboards as kb
from data.save_product import load_atb_products_from_csv, search_in_products



router = Router()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "parsers/atb")
DATA_FILE = os.path.join(DATA_DIR, "atb_products.csv")



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f"Привіт!\n Давай прозпочнемо!\n Обери магазин:",
    reply_markup=kb.buttons)

@router.message(Command("profile"))
async def my_profile(message: Message):
    print(f"User {message.from_user.id} started the conversation.")
    await message.reply(
        f"Привіт!\nТвій ID:{message.from_user.id}\nІмя: {message.from_user.first_name}",
    reply_markup=kb.settings)


@router.message(F.text == "help")
async def get_help(message: Message):
    await message.answer("Це команда /help")


@router.message(lambda message: message.text != "Обрати магазин")
async def search_product(message: types.Message):
    query = message.text
    # Тут логіка пошуку товарів по назві query
    results = search_in_products(query)
    if results:
        await message.answer(f"Знайдено товари за '{query}':\n" + "\n".join(results))
    else:
        await message.answer(f"Товарів за '{query}' не знайдено.")


@router.message(F.text == "Обрати магазин")
async def how_are_you(message: Message):
    await message.answer("🔍", reply_markup=kb.shop)



@router.callback_query(lambda callback_query: callback_query.data.startswith("favorite_"))
async def add_to_favorites(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    product_title = callback_query.data.split("_", 1)[1]

    if user_id not in kb.user_favorites:
        kb.user_favorites[user_id] = []

    if product_title not in kb.user_favorites[user_id]:
        kb.user_favorites[user_id].append(product_title)


    await callback_query.answer(f"Товар '{product_title}' додано в обрані!")





@router.message(F.text == "Обрані товари")
async def show_favorites(message: types.Message):
    user_id = str(message.from_user.id)
    favorites = kb.user_favorites.get(user_id, [])

    if favorites:
        favorites_message = "Ваші обрані товари:\n" + "\n".join(favorites)
        print("user_favorites:", kb.user_favorites)
        print("user_id:", user_id)
        print("favorites:", favorites)
    else:
        favorites_message = "У вас немає обраних товарів."

    await message.answer(favorites_message, reply_markup=kb.buttons)


@router.callback_query(F.data.startswith("shop-atb"))
async def show_products(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split("-")
    offset = int(parts[2]) if len(parts) == 3 else 0  # shop-atb vs shop-atb-5
    products = load_atb_products_from_csv(DATA_FILE)
    step = 5
    current_batch = products[offset:offset + step]

    try:
        for product in current_batch:
            sanitized_title = re.sub(r'[^\w\s-]', '_', product.title).strip()
            max_title_length = 30
            shortened_title = sanitized_title[:max_title_length]

            caption = f"📦<b>{product.title}</b>\n"
            caption += f"\n"
            caption += f"💰 <b>{product.price} грн</b>{' ' * 20}<s>{product.old_price} грн</s>\n"



            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Додати в обране",
                        callback_data=f"favorite_{shortened_title}"
                    )
                ]
            ])
            print(kb.user_favorites)

            if getattr(product, "image_url", None):
                await callback.message.answer_photo(
                    photo=product.image_url,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup = keyboard
                )
            else:
                await callback.message.answer(
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            await asyncio.sleep(1)

        if offset + step < len(products):
            next_offset = offset + step
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬇️ Показати ще",
                    callback_data=f"shop-atb-{next_offset}"
                )]
            ])
            await callback.message.answer("⬇️ Ще товари:", reply_markup=keyboard)
    except Exception as e:
        await callback.message.answer("⚠️ Не вдалося завантажити товари.")
        print(f"Помилка парсингу: {e}")










# def search_in_products(query: str):
#     """
#     Search for products by name
#
#     Args:
#         query (str): Search query string
#
#     Returns:
#         list: List of formatted product strings that match the query
#     """
#     products = load_atb_products_from_csv(DATA_FILE)
#     results = []
#
#     # Convert query to lowercase for case-insensitive search
#     query = query.lower()
#
#     for product in products:
#         if query in product.title.lower():
#             # Format the product as a string
#             product_str = f"📦 {product.title} - 💰 {product.price} грн (було {product.old_price} грн)"
#             results.append(product_str)
#
#     return results





# @router.callback_query(F.data == "ATB")
# async def catalog(callback: CallbackQuery):
#     await callback.answer("Виберіть товари:", show_alert=True)
#     await callback.message.answer("Товари ATB:")

# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     print(f"User {message.from_user.id} started the conversation.")
#     # await message.reply(
#     #     f"Привіт!\n Давай прозпочнемо!\n Обери магазин:",
#     # reply_markup=kb.shop)
#
#     await message.reply(
#         f"Привіт!\n Давай прозпочнемо!\n Обери магазин:",
#         reply_markup=await kb.inline_shops())
