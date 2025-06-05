import os
import urllib.parse
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

from database import User, SessionLocal, init_db
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Поделиться номером", request_contact=True))
    await msg.answer("Привет! Поделитесь номером телефона для входа:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(msg: types.Message):
    phone = msg.contact.phone_number
    user_id = msg.from_user.id

    async with SessionLocal() as session:
        existing_user = await session.get(User, user_id)
        if not existing_user:
            new_user = User(telegram_id=user_id, phone=phone)
            session.add(new_user)
            await session.commit()

    await show_main_menu(msg)

async def show_main_menu(msg: types.Message):
    uid = msg.from_user.id
    planner_url = f"https://yourdomain.com/planner?uid={uid}"

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📝 Заметка", callback_data="note"),
        InlineKeyboardButton("⏰ Будильник", callback_data="alarm")
    )
    kb.add(
        InlineKeyboardButton("📅 Планер", url=planner_url),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    await msg.answer("Выберите действие:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "note")
async def note_callback(call: types.CallbackQuery):
    url = "shortcuts://run-shortcut?" + urllib.parse.urlencode({
        "name": "Добавить заметку",
        "input": "text",
        "text": "Новая заметка"
    })
    await call.message.answer(f"Нажмите для создания заметки:\n{url}")

@dp.callback_query_handler(lambda c: c.data == "alarm")
async def alarm_callback(call: types.CallbackQuery):
    url = "shortcuts://run-shortcut?" + urllib.parse.urlencode({
        "name": "Установить будильник",
        "input": "text",
        "text": "08:00 | Проснуться"
    })
    await call.message.answer(f"Нажмите для установки будильника:\n{url}")

@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            text = f"👤 Ваш профиль:\nTelegram ID: {user.telegram_id}\nТелефон: {user.phone}\nУстройств: 1"
        else:
            text = "Профиль не найден."
    await call.message.answer(text)

if __name__ == "__main__":
    asyncio.run(init_db())
    executor.start_polling(dp)
