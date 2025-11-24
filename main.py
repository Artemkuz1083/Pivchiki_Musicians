import logging
import os
from dotenv import load_dotenv
from asyncio import run
from aiogram import Bot, Dispatcher
from handlers import start
from handlers.band.band_profile import edit_band_profile
from handlers.band.band_registration import band_registration
from handlers.profile import profile
from handlers.registration import registration
from database.session import init_db
from handlers.show_profiles.with_registration import with_registration
from handlers.show_profiles.without_registration import without_registration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.info("🔥 ЛОГИ РАБОТАЮТ!")

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await init_db()
    dp.include_router(registration.router)
    dp.include_router(profile.router)
    dp.include_router(band_registration.router)
    dp.include_router(edit_band_profile.router)
    dp.include_router(start.router)
    dp.include_router(without_registration.router)
    #dp.include_router(with_registration.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен")
    run(main())