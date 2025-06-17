from aiogram import  F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
import bot.keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"User {message.from_user.id} started the conversation.")
    # await message.reply(
    #     f"Привіт!\n Давай прозпочнемо!\n Обери магазин:",
    # reply_markup=kb.shop)

    await message.reply(
        f"Привіт!\n Давай прозпочнемо!\n Обери магазин:",
        reply_markup=await kb.inline_shops())





@router.callback_query(F.data == "ATB")
async def catalog(callback: CallbackQuery):
    await callback.answer("Виберіть товари:", show_alert=True)
    await callback.message.answer("Товари ATB:")


async def my_profile(message: Message):
    print(f"User {message.from_user.id} started the conversation.")
    await message.reply(
        f"Привіт!\nТвій ID:{message.from_user.id}\nІмя: {message.from_user.first_name}",
    reply_markup=kb.settings)


@router.message(Command("profile"))
async def my_profile(message: Message):
    print(f"User {message.from_user.id} started the conversation.")
    await message.reply(
        f"Привіт!\nТвій ID:{message.from_user.id}\nІмя: {message.from_user.first_name}",
    reply_markup=kb.settings)


@router.message(Command("help"))
async def get_help(message: Message):
    await message.answer("Це команда /help")

@router.message(F.text == "Як справи?")
async def how_are_you(message: Message):
    await message.answer("Оберіть магазин:", reply_markup=kb.shop)