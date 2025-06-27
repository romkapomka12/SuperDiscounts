import asyncio
from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import bot.keyboards as kb
from bot.favorites_manager import load_favorites, save_favorites
# from data.save_product import load_atb_products_from_csv, search_in_products
from config import logger
from collections import defaultdict
from data.db_manager import search_products_in_db

router = Router()




ALL_PRODUCTS_LIST = []
PRODUCTS_BY_ID = {}




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

    for fav_item in favorites:
        # Використовуємо збережені дані без пошуку в CSV
        message_text = (
            f"📦 <b>{fav_item['title']}</b>\n"
            f"💰 <b>{fav_item['price']} грн</b>\n"
            f"🏬 <b>{fav_item['tag_shop']}</b>\n"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Видалити з обраних",
                    callback_data=f"remove_{fav_item['product_id']}"
                )
            ]
        ])

        await message.answer(
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("favorite_"))
async def add_to_favorites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    product_id = callback.data.split("favorite_")[1]

    # Шукаємо товар в нашому завантаженому словнику
    product_to_add = PRODUCTS_BY_ID.get(product_id)

    if not product_to_add:
        await callback.answer("Помилка: товар не знайдено.")
        return


    favorites = load_favorites(user_id)

    if not any(p.get("product_id") == product_id for p in favorites):
        favorites.append({
            "product_id": product_to_add['id'],
            "title": product_to_add['title'],
            "price": product_to_add['price'],
            "tag_shop": product_to_add['tag_shop'],
            "image_url": product_to_add['image_url']
        })
        save_favorites(user_id, favorites)
        await callback.answer(f"Товар '{product_to_add['title'][:30]}...' додано до обраних!")
    else:
        await callback.answer("Цей товар вже є в обраних")


@router.callback_query(F.data.startswith("remove_"))
async def remove_from_favorites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    product_id = callback.data.split("remove_")[1]

    favorites = load_favorites(user_id)
    updated_favorites = [p for p in favorites if p["product_id"] != product_id]

    if len(updated_favorites) < len(favorites):
        save_favorites(user_id, updated_favorites)
        await callback.answer("Товар видалено з обраних!")
        await callback.message.delete()
    else:
        await callback.answer("Цього товару вже немає в обраних")


@router.message(lambda message: message.text not in ["Обрати магазин", "Обрані товари"])
async def search_product(message: types.Message):
    query = message.text
    if len(query) < 3:
        await message.answer("Будь ласка, введіть запит довжиною не менше 3 символів.")
        return

    results = search_products_in_db(query)

    if not results:
        await message.answer(f"На жаль, за запитом '{query}' нічого не знайдено.")
        return

    # Групуємо товари за назвою. defaultdict(list) - дуже зручна річ для цього
    grouped_products = defaultdict(list)
    for product in results:
        # Тут можна застосувати ще кращу логіку групування,
        # наприклад, по перших 2-3 словах назви
        key = ' '.join(product['normalized_title'].split()[:3])
        grouped_products[key].append(product)

    await message.answer(f"🔍 Знайдено результати за запитом '{query}':")

    response_text = ""
    for group_key, products_in_group in grouped_products.items():
        # Беремо найповнішу назву з групи для заголовка
        title_for_display = sorted(products_in_group, key=lambda x: len(x['title']), reverse=True)[0]['title']
        response_text += f"\n🛒 <b>{title_for_display}</b>\n"

        # Сортуємо за ціною, щоб показати найдешевшу пропозицію першою
        for product in sorted(products_in_group, key=lambda x: x['price']):
            response_text += f"  - <b>{product['tag_shop']}</b>: {product['price']:.2f} грн\n"

        # Щоб повідомлення не було занадто довгим
        if len(response_text) > 3500:
            await message.answer(response_text, parse_mode="HTML")
            response_text = ""

    if response_text:
        await message.answer(response_text, parse_mode="HTML")


@router.callback_query(F.data.startswith("shop-atb"))
async def show_products(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split("-")
    offset = int(parts[2]) if len(parts) == 3 else 0
    step = 5
    products_to_show = [p for p in ALL_PRODUCTS_LIST if p['tag_shop'] == 'АТБ-Маркет']
    current_batch = products_to_show[offset:offset + step]

    try:
        if not current_batch:
            await callback.message.answer("Більше товарів немає.")
            return

        for product in current_batch:  # 'product' - це СЛОВНИК
            # --- ВИПРАВЛЕННЯ ТУТ: використовуємо доступ за ключем ['key'] ---

            # Назва для callback_data - просто ID, він вже унікальний
            product_id = product['id']
            product_title = product['title']
            product_price = product['price']
            product_old_price = product['old_price']
            product_date = product['date']
            product_image = product['image_url']
            product_shop = product['tag_shop']

            caption = f"🏷️  <b>{product_title}</b>\n\n"
            caption += f"💰 <b>{product_price} грн</b>{' ' * 20}<s>📉{product_old_price} грн</s>\n\n"
            caption += f"<i>📅  {product_date} </i>"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💖 Додати в обране",
                        callback_data=f"favorite_{product_id}"  # Передаємо тільки ID
                    )
                ]
            ])

            logger.info(f"Показуємо: {product_title}, {product_price}, {product_shop}")

            # Перевіряємо наявність картинки і відправляємо
            if product_image:
                await callback.message.answer_photo(
                    photo=product_image,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                await callback.message.answer(
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            await asyncio.sleep(0.3)  # Можна трохи зменшити затримку

        # Перевірка, чи є ще товари для показу
        if offset + step < len(products_to_show):
            next_offset = offset + step
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬇️ Показати ще",
                    callback_data=f"shop-atb-{next_offset}"
                )]
            ])
            await callback.message.answer(text="⬇️ Ще товари:", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Помилка у show_products: {e}", exc_info=True)
        await callback.message.answer("⚠️ Не вдалося завантажити товари.")


