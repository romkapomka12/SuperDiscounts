import asyncio
import os
import re
from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import bot.keyboards as kb
from bot.favorites_manager import load_favorites, save_favorites
from data.save_product import load_atb_products_from_csv, search_in_products
from config import logger


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


@router.message(F.text == "Обрати магазин")
async def how_are_you(message: Message):
    await message.answer("🔍", reply_markup=kb.shop)


@router.message(F.text == "Обрані товари")
async def show_favorites(message: types.Message):
    user_id = str(message.from_user.id)
    favorites = load_favorites(user_id)

    if not favorites:
        await message.answer("📭 У вас немає обраних товарів.", reply_markup=kb.buttons)
        return

    await message.answer(f"💖 Ваші обрані товари ({len(favorites)}):")

    for product in favorites:
        message_text = (f""
                        f"📦 <b>{product['title']}</b>\n"
                        f"💰 <b>{product['price']} грн</b>\n"
                        f"🏬 <b>{product['tag_shop']}</b>"
                        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Видалити з обраних",
                    callback_data=f"remove_{product['title']}"
                )
            ]
        ])

        await message.answer(
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("remove_"))
async def remove_from_favorites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    product_title = callback.data.split("remove_")[1]

    favorites = load_favorites(user_id)
    logger.info(f"favorites")

    updated_favorites = [p for p in favorites if p["title"] != product_title]

    save_favorites(user_id, updated_favorites)
    await callback.answer(f"Товар '{product_title}' видалено!")
    await callback.message.delete()


@router.callback_query(F.data.startswith("favorite_"))
async def add_to_favorites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    product_data = callback.data.split("favorite_")[1]

    if "|" not in product_data:
        await callback.answer("Помилка: некоректні дані товару")
        return

    product_title, product_price, tag_shop = product_data.split("|", maxsplit=2)
    logger.info(
        f"product_title: {product_title}, product_price: {product_price}, tag_shop: {tag_shop}"
    )

    favorites = load_favorites(user_id)

    # Додаємо словник у список обраних
    favorites.append({
        "title": product_title,
        "price": product_price,
        "tag_shop": tag_shop
    })

    save_favorites(user_id, favorites)
    await callback.answer(f"Товар '{product_title}' додано до обраних!")

    # Перевіряємо, чи товар вже є в обраних
    if not any(p["title"] == product_title for p in favorites):
        favorites.append({
            "title": product_title,
            "price": product_price,
            "tag_shop": tag_shop
        })
        save_favorites(user_id, favorites)
        await callback.answer(f"Товар '{product_title}' додано до обраних!")
    else:
        await callback.answer("Цей товар вже є в обраних")



@router.message(lambda message: message.text != "Обрати магазин")
async def search_product(message: types.Message):
    query = message.text
    # Тут логіка пошуку товарів по назві query
    results = search_in_products(query)
    if results:
        await message.answer(f"Знайдено товари за '{query}':\n" + "\n".join(results))
    else:
        await message.answer(f"Товарів за '{query}' не знайдено.")


@router.callback_query(F.data.startswith("shop-atb"))
async def show_products(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split("-")
    offset = int(parts[2]) if len(parts) == 3 else 0
    products = load_atb_products_from_csv(DATA_FILE)
    step = 5
    current_batch = products[offset:offset + step]

    try:
        for product in current_batch:
            sanitized_title = re.sub(r'[^\w\s-]', '_', product.title).strip()
            max_title_length = 15
            shortened_title = sanitized_title[:max_title_length]

            caption = f"🏷️  <b>{product.title}</b>\n"
            caption += f"\n"
            caption += f"💰 <b>{product.price} грн</b>{' ' * 20}<s>📉{product.old_price} грн</s>\n"
            caption += f"\n"
            caption += f"<i>📅  {product.date} </i>"


            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Додати в обране",
                        callback_data=f"favorite_{shortened_title}|{product.price}|{product.tag_shop}"
                    )
                ]
            ])
            logger.info(f"{product.title}, {product.price}, {product.tag_shop}")

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
            await asyncio.sleep(0.5)

        if offset + step < len(products):
            next_offset = offset + step
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬇️ Показати ще",
                    callback_data=f"shop-atb-{next_offset}"
                )]
            ])
            await callback.message.answer(text = "⬇️ Ще товари:", reply_markup=keyboard)
    except Exception as e:
        await callback.message.answer("⚠️ Не вдалося завантажити товари.")
        print(f"Помилка парсингу: {e}")






# @router.message(F.text == "Обрані товари")
# async def show_favorites(message: types.Message):
#     user_id = message.from_user.id
#     favorites = load_favorites(user_id)
#
#     if not favorites:
#         await message.answer("📭 У вас немає обраних товарів.", reply_markup=kb.buttons)
#         return
#
#     await message.answer(f"💖 Ваші обрані товари ({len(favorites)}):")
#
#     for product_title in favorites:
#         # Створюємо клавіатуру з кнопкою видалення
#         keyboard = InlineKeyboardMarkup(inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="❌ Видалити з обраних",
#                     callback_data=f"remove_{product_title}"
#                 )
#             ]
#         ])
#
#         await message.answer(
#             f"📦 {product_title}",
#             reply_markup=keyboard
#         )




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
