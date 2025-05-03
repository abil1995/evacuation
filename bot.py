import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_BOT_TOKEN = "7905215429:AAF-OL390x9BlYit-WAbY0miSqwkGwgqQJI"
DGIS_API_KEY = "71a15a9d-dd13-4d5f-8181-566b38ffb284"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def search_evacuation_points(latitude, longitude):
    search_queries = [
        "Пункт сбора, эвакуации и временного размещения населения",
        "Эвакуационный пункт",
        "Пункт временного размещения",
        "Пункт эвакуации"
    ]

    url = "https://catalog.api.2gis.com/3.0/items"
    async with aiohttp.ClientSession() as session:
        for query in search_queries:
            params = {
                "q": query,
                "location": f"{longitude},{latitude}",
                "key": DGIS_API_KEY
            }
            async with session.get(url, params=params) as response:
                data = await response.json()

                if data.get("result", {}).get("items"):
                    first_result = data["result"]["items"][0]
                    address = first_result["address_name"]
                    object_id = first_result.get("id")
                    link = f"https://2gis.kz/mangistau/geo/{object_id}" if object_id else "Ссылка отсутствует"
                    return f"Ближайший пункт: {address}\n🔗 [Открыть в 2ГИС]({link})"

    return "Извините, ближайший пункт эвакуации не найден."

@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True
    )
    await message.answer("Отправьте или прикрепите свою геолокацию, чтобы найти ближайший пункт эвакуации.", reply_markup=keyboard)

@dp.message(lambda message: message.location is not None)
async def handle_location(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    result = await search_evacuation_points(latitude, longitude)
    await message.answer(result, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
