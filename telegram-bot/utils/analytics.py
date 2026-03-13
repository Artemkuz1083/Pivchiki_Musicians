import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import httpx
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

load_dotenv()

POST_API_KEY = os.getenv("APPMETRICA_POST_API_KEY")
APP_ID = os.getenv("APPMETRICA_APP_ID")

async def track_event(user_id: int, event_name: str, params: dict = None):
    url = "https://api.appmetrica.yandex.ru/logs/v1/import/events"

    query_params = {
        "application_id": APP_ID,
        "import_api_key": POST_API_KEY,
        "event_name": event_name,
        "profile_id": str(user_id),
        "event_json": json.dumps(params) if params else "{}",
        "event_timestamp": int(datetime.now().timestamp())
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, params=query_params)

            if response.status_code in [200, 202]:
                logging.info(f"УРА! Статус {response.status_code}.")
            else:
                logging.error(f"Ошибка {response.status_code}: {response.text}")
        except Exception as e:
            logging.error(f"Ошибка в Docker: {e}")


class AnalyticsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user:
            if isinstance(event, Message):
                # Фиксируем текст (для North Star: начало воронки)
                await track_event(user.id, "user_message", {"text": event.text[:20] if event.text else "media"})
            elif isinstance(event, CallbackQuery):
                # Фиксируем нажатия кнопок (для North Star: переходы по воронке)
                await track_event(user.id, "callback_click", {"data": event.data})

        return await handler(event, data)