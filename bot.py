
import os
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging

# Загрузка переменных окружения
load_dotenv()

# Инициализация логгера
logging.basicConfig(level=logging.INFO)

# Получение токенов из переменных окружения
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка наличия токенов
if not all([API_KEY, API_SECRET, TELEGRAM_BOT_TOKEN]):
    raise ValueError("Отсутствуют необходимые API-ключи или токены!")

# Создание клиента Binance
client = Client(API_KEY, API_SECRET)

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Пример команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Добро пожаловать! Этот бот позволяет отправлять торговые сигналы. 🚀")

# Пример функции обработки сигнала
async def send_signal(signal):
    try:
        caption = (
            f"📊 Сигнал на сделку:
"
            f"Монета: {signal['symbol']}
"
            f"Вход: {signal['entry']:.4f}
"
            f"TP (тейк-профит): {signal['tp']:.4f}
"
            f"SL (стоп-лосс): {signal['sl']:.4f}
"
            f"Вероятность успеха: {signal['probability']}%
"
            f"Время сделки: {signal['time_to_hold']}
"
        )
        # Здесь укажите ID чата или используйте message.chat.id
        chat_id = 123456789  
        await bot.send_photo(chat_id=chat_id, photo=signal['image_url'], caption=caption)
    except Exception as e:
        logging.error(f"Ошибка при отправке сигнала: {e}")

# Основная функция
if __name__ == "__main__":
    try:
        logging.info("Бот запускается...")
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.critical(f"Критическая ошибка: {e}")
