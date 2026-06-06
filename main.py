import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8903608111:AAFP7AIAhNxdUZC64DunwoEirvJXagX5-10"
CRYPTO_PAY_TOKEN = "590296:AAoW0FE3wdGPIe7VDhjt4FIhbMfZQo1KDU5"
GROUP_ID = "-1003880020106"
SUPPORT_USER = "LegalWork_Online"
DONATE_URL = "https://donatello.to/VpiskaPL"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class States(StatesGroup):
    username = State()
    screenshot = State()

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="ℹ️ Инфо"), KeyboardButton(text="🖼 Галерея")],
        [KeyboardButton(text="🎟 Купить билет"), KeyboardButton(text="💬 Поддержка")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    text = text = (
    "Привет! 👋 Это VpiskaPL — твой пропуск на самые закрытые тусовки Варшавы!\n\n"
    "Мы организуем Private Party для своих. Никаких случайных людей — только топовая компания и правильная атмосфера.\n\n"
    "Ближайшая вписка состоится в следующую субботу! 📅\n\n"
    "🎟 Стоимость участия: $15.\n"
    "Что входит в цену:\n"
    "• Личное приглашение и доступ к закрытому мероприятию.\n"
    "• Уникальный QR-код для входа (придет в бот после оплаты).\n"
    "• Адрес локации — сообщим ровно за 24 часа до старта.\n\n"
    "Жми кнопку ниже, чтобы забронировать место, или переходи в «Инфо», чтобы узнать правила нашего комьюнити. 🚀"
)
    if os.path.exists("start.jpg"):
        await message.answer_photo(photo=FSInputFile("start.jpg"), caption=text, reply_markup=get_main_kb())
    else:
        await message.answer(text, reply_markup=get_main_kb())

@dp.message(F.text == "ℹ️ Инфо")
async def info(message: Message):
    text = (
        "ℹ️ Всё, что нужно знать о VpiskaPL:\n\n"
        "Формат мероприятий: Мы проводим закрытые тематические вечеринки в Варшаве. Наш формат — Private Party.\n\n"
        "Как попасть на вписку?\n"
        "• Оплата: 15 долларов.\n"
        "• Пропуск: После оплаты придет QR-код.\n"
        "• Локация: Адрес сообщаем за 24 часа до начала.\n\n"
        "Правила входа: При входе предъяви QR-код. Код одноразовый!"
        "Наши девушки скрасять досуг одиноким парням!"
        "И у Нас много чего интересного 🐈‍⬛"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Купить билет", callback_data="buy_ticket")],
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USER}")]
    ])
    if os.path.exists("info.jpg"):
        await message.answer_photo(photo=FSInputFile("info.jpg"), caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

@dp.message(F.text == "🎟 Купить билет")
@dp.callback_query(F.data == "buy_ticket")
async def ask_username(event, state: FSMContext):
    msg = event.message if hasattr(event, 'message') else event
    await msg.answer("Введите ваш Telegram-ник (например, @username):")
    await state.set_state(States.username)

@dp.message(States.username)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 ОПЛАТИТЬ 15 USDT", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="💳 Оплата картой", url=DONATE_URL)],
        [InlineKeyboardButton(text="✅ Оплатил, прислать скрин", callback_data="pay_done")]
    ])
    await message.answer("Выберите способ оплаты:", reply_markup=kb)
    await state.set_state(States.screenshot)

@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: Message):
    async with aiohttp.ClientSession() as session:
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
        async with session.post(url, json={"asset": "USDT", "amount": "15.0"}, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok"):
                await callback.message.answer(f"Ссылка: {data['result']['pay_url']}")

@dp.callback_query(F.data == "pay_done")
async def ask_photo(callback: Message):
    await callback.message.answer("Пришлите скриншот оплаты:")

@dp.message(States.screenshot, F.photo)
async def get_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_photo(GROUP_ID, photo=message.photo[-1].file_id, 
                         caption=f"⚡️ Оплата от @{message.from_user.username}\nНик: {data.get('user_name', 'Нет')}")
    await message.answer("Скриншот принят!")
    await state.clear()

@dp.message(F.text == "🖼 Галерея")
async def gallery(message: Message):
    folder = "gallery"
    if os.path.exists(folder) and os.path.isdir(folder):
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.png'))]
        if files:
            for f in files[:10]:
                await message.answer_photo(photo=FSInputFile(f))
        else:
            await message.answer("Галерея пуста.")
    else:
        await message.answer("Папка 'gallery' не найдена. Создайте её рядом с main.py.")

@dp.message(F.text == "💬 Поддержка")
async def support(message: Message):
    await message.answer(f"Пиши сюда: https://t.me/{SUPPORT_USER}")

async def main():
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())