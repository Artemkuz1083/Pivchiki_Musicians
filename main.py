import os
from dotenv import load_dotenv
from asyncio import run
from aiogram import Bot, Dispatcher
from handlers import start
from handlers.registration import registration
from database.session import init_db

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await init_db()

    dp.include_router(registration.router)
    dp.include_router(start.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен")
    run(main())