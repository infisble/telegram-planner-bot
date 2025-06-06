import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, Contact
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy import select
from dotenv import load_dotenv

from database import init_db, async_session
from models import User

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

# --- Инициализация бота ---
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# --- Клавиатуры ---
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Поделиться номером", request_contact=True)],
    ],
    resize_keyboard=True
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Заметка"), KeyboardButton(text="⏰ Будильник")],
        [KeyboardButton(text="📅 Планер"), KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True
)

# --- Хендлеры ---

@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Привет! Поделись номером телефона, чтобы начать ⬇️", reply_markup=start_kb)


@dp.message(F.contact)
async def contact_handler(message: Message):
    contact: Contact = message.contact
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.phone = contact.phone_number
        else:
            user = User(telegram_id=user_id, phone=contact.phone_number)
            session.add(user)

        await session.commit()

    await message.answer("✅ Телефон получен! Вот главное меню:", reply_markup=main_kb)


@dp.message(F.text == "📝 Заметка")
async def note_handler(message: Message):
    await message.answer("Напиши текст заметки (заглушка).")


@dp.message(F.text == "⏰ Будильник")
async def alarm_handler(message: Message):
    await message.answer("Укажи время для будильника (заглушка).")


@dp.message(F.text == "📅 Планер")
async def planner_handler(message: Message):
    await message.answer("Планер будет доступен в веб-приложении.\n(заглушка на будущее)")


@dp.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

    if user:
        await message.answer(
            f"👤 <b>Профиль</b>:\n\n"
            f"Telegram ID: <code>{user.telegram_id}</code>\n"
            f"Телефон: <code>{user.phone}</code>"
        )
    else:
        await message.answer("❌ Пользователь не найден. Сначала отправь свой номер.")


# --- Запуск бота ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
