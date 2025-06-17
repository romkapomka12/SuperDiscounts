from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pandas.core.dtypes.cast import construct_1d_arraylike_from_scalar

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Catalog", callback_data="catalog")],
    [InlineKeyboardButton(text="Musor", callback_data="basket"),
    InlineKeyboardButton(text="Contact", callback_data="contacts")]
])


settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="Выйти", callback_data="exit")]
])

shop = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="АТБ", callback_data="shop_atb")],
    [InlineKeyboardButton(text="Новус", callback_data="shop_novus")],
    [InlineKeyboardButton(text="Сільпо", callback_data="shop_silpo")],
    [InlineKeyboardButton(text="Фора", callback_data="shop_fora")],
    [InlineKeyboardButton(text="Всі магазини", callback_data="shop_fora")]
])

shops = ["ATB", "NOVUS", "SILPO", "FORA", "Всі магазины"]

async  def inline_shops():
    keyboard = InlineKeyboardBuilder()
    for shop in shops:
        keyboard.add(InlineKeyboardButton(text=shop, callback_data=shop))
    return keyboard.adjust(2).as_markup()


