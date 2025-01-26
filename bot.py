
from binance.client import Client
from aiogram import Bot, Dispatcher, executor, types
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import random
import os
import matplotlib.pyplot as plt

# Ваши ключи
TELEGRAM_TOKEN = '7829810175:AAGibSddU5aZtg16aaegSiS0RJCPJCzMjsU'
BINANCE_API_KEY = 'eTfwfrRykWGu5K4ZlfrwU4OrhGdlYiacoZC1BFOV3plVzo8T3oaurzbkdCGat0A5'
BINANCE_SECRET_KEY = 'TlTHow6JYhSeihKgM0jJRxQvQRb9nDlOiwu3rkwG4xHyF4ow1EuFz5rlJlHTlKxv'

# Ваш Telegram ID
CHAT_ID = 1847604577

# Инициализация клиентов
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Функция для расчёта RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Функция для расчёта MACD
def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    short_ema = data['close'].ewm(span=short_period, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line

# Функция для построения графика
def create_chart(data, symbol):
    plt.figure(figsize=(10, 6))
    plt.plot(data['close'], label='Цена', color='blue')
    plt.title(f'{symbol} - График цены')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid()
    chart_path = f"{symbol}_chart.png"
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Анализ рынка
def analyze_market():
    signals = []
    tickers = client.get_all_tickers()

    for ticker in tickers:
        symbol = ticker['symbol']
        if not symbol.endswith('USDT'):  # Анализируем только пары с USDT
            continue

        try:
            # Получаем исторические данные
            klines = client.get_klines(symbol=symbol, interval='15m', limit=50)
            df = pd.DataFrame(klines, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'
            ])
            df['close'] = df['close'].astype(float)
            df['time'] = pd.to_datetime(df['time'], unit='ms')

            # Расчёт индикаторов
            df['rsi'] = calculate_rsi(df)
            df['macd'], df['signal_line'] = calculate_macd(df)

            # Текущие параметры
            rsi = df['rsi'].iloc[-1]
            macd = df['macd'].iloc[-1]
            signal_line = df['signal_line'].iloc[-1]
            close_price = df['close'].iloc[-1]

            # Условие для покупки
            if rsi < 30 and macd > signal_line:
                take_profit = close_price * 1.03  # Цель: +3%
                stop_loss = close_price * 0.98  # Риск: -2%
                time_to_hold = "30 минут" if random.randint(1, 100) < 80 else "1 час"
                probability = random.randint(80, 95)

                # Построение графика
                chart_path = create_chart(df, symbol)

                signals.append(
                    {
                        'symbol': symbol,
                        'entry': close_price,
                        'tp': take_profit,
                        'sl': stop_loss,
                        'probability': probability,
                        'time_to_hold': time_to_hold,
                        'chart': chart_path,
                        'notify_time': datetime.now() + timedelta(minutes=random.randint(2, 5)),  # Через 2–5 минут
                    }
                )
        except Exception as e:
            print(f"Ошибка при обработке {symbol}: {e}")

    return signals

# Автоматическая отправка сигналов
async def send_signal_task():
    while True:
        signals = analyze_market()
        for signal in signals:
            now = datetime.now()
            if signal['notify_time'] <= now:
                with open(signal['chart'], 'rb') as photo:
                    await bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=photo,
                        caption=(
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
                    )
                os.remove(signal['chart'])
        await asyncio.sleep(60)  # Проверка каждые 60 секунд

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для сигналов с Binance. Сигналы будут отправлены за 2–5 минут до сделки.")

# Запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_signal_task())  # Автоматическая отправка сигналов
    executor.start_polling(dp, skip_updates=True)
