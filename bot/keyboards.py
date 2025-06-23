from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


buttons = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Обрати магазин")],[KeyboardButton(text="Обрані товари")]


],
                     resize_keyboard=True,
                     input_field_placeholder="пошук товарів")


settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="Выйти", callback_data="exit")]
])

shop = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="АТБ", callback_data="shop-atb")],
    [InlineKeyboardButton(text="Новус", callback_data="shop_novus")],
    [InlineKeyboardButton(text="Сільпо", callback_data="shop_silpo")],
    [InlineKeyboardButton(text="Фора", callback_data="shop_fora")],
    [InlineKeyboardButton(text="Всі магазини", callback_data="shop_fora")]
])
