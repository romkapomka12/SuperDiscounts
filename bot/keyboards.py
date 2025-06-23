from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pandas.core.dtypes.cast import construct_1d_arraylike_from_scalar

# main = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="АТБ", callback_data="shop-atb")],
#     [InlineKeyboardButton(text="Новус", callback_data="shop-novus")],
#     [InlineKeyboardButton(text="Сільпо", callback_data="shop-silpo")],
#     [InlineKeyboardButton(text="Фора", callback_data="shop-fora")],
#     [InlineKeyboardButton(text="Всі магазини", callback_data="shop-all")]
# ])

user_favorites = {}

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

# shops = ["ATB", "NOVUS", "SILPO", "FORA", "Всі магазины"]

# async  def inline_shops():
#     keyboard = InlineKeyboardBuilder()
#     for shop in shops:
#         keyboard.add(InlineKeyboardButton(text=shop, callback_data=shop))
#     return keyboard.adjust(2).as_markup()



