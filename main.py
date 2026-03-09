import logging
import os
from dotenv import load_dotenv
from asyncio import run
from aiogram import Bot, Dispatcher
from handlers import start
from handlers.band.band_profile import edit_band_profile
from handlers.band.band_registration import band_registration
from handlers.likes import likes
from handlers.match import match
from handlers.profile import profile
from handlers.registration import registration
from database.session import init_db
from handlers.show_profiles import show_profiles
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.info("🔥 ЛОГИ РАБОТАЮТ!")

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def main():
    await init_db()
    dp.update.outer_middleware(AnalyticsMiddleware())
    dp.include_router(registration.router)
    dp.include_router(profile.router)
    dp.include_router(band_registration.router)
    dp.include_router(edit_band_profile.router)
    dp.include_router(start.router)
    dp.include_router(show_profiles.router)
    dp.include_router(likes.router)
    dp.include_router(match.router)
    await dp.start_polling(bot)

import asyncio
from utils.analytics import track_event, AnalyticsMiddleware  # Импортируй свою функцию

async def test():
    print("Отправка тестового события...")
    await track_event(user_id=12345, event_name="test_connection", params={"status": "working"})
    print("Готово! Проверь вкладку 'События' в AppMetrica через 5-10 минут.")

if __name__ == "__main__":
    asyncio.run(test())

if __name__ == "__main__":
    print("Бот запущен")
    run(main())