import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Contact
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from dotenv import load_dotenv

from database import async_session, init_db
from models import User

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Bot and Dispatcher ---
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- Keyboards ---
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

# --- Handlers ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Поделись номером телефона, чтобы начать ⬇️", reply_markup=start_kb)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
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

@dp.message_handler(lambda msg: msg.text == "📝 Заметка")
async def handle_note(message: types.Message):
    await message.answer("Напиши текст заметки (заглушка).")

@dp.message_handler(lambda msg: msg.text == "⏰ Будильник")
async def handle_alarm(message: types.Message):
    await message.answer("Укажи время для будильника (заглушка).")

@dp.message_handler(lambda msg: msg.text == "📅 Планер")
async def handle_planner(message: types.Message):
    await message.answer("Планер будет доступен в веб-приложении.\n(заглушка на будущее)")

@dp.message_handler(lambda msg: msg.text == "👤 Профиль")
async def handle_profile(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

    if user:
        await message.answer(
            f"👤 Профиль:\n\n"
            f"Telegram ID: <code>{user.telegram_id}</code>\n"
            f"Телефон: <code>{user.phone}</code>"
        )
    else:
        await message.answer("❌ Пользователь не найден. Сначала отправь свой номер.")

# --- Startup ---
async def on_startup(_):
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущен!")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
