import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
import httpx
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

# load_dotenv()
#
# secret_key = os.getenv("SECRET_KEY")
# measurement_id = os.getenv("MEASUREMENT_ID")

# async def track_event(user_id: int, event_name: str, params: dict = None):
#     url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={secret_key}"
#
#     payload = {
#         "client_id": f"{user_id}.{int(time.time())}",
#         "events": [
#             {
#                 "name": event_name,
#                 "params": {
#                     "engagement_time_msec": 100,
#                     "platform": "telegram",
#                     "message": "господь помоги"
#                 }
#             }
#         ]
#     }
#
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         try:
#             response = await client.post(url, json=payload)
#
#             if response.status_code == 204:
#                 logging.info("GA event sent successfully")
#             else:
#                 logging.error(f"GA error {response.status_code}: {response.text}")
#
#         except Exception as e:
#             logging.error(f"Analytics error: {e}")
#
#
# class AnalyticsMiddleware(BaseMiddleware):
#     async def __call__(self, handler, event, data):
#         user = data.get("event_from_user")
#         if user:
#             if isinstance(event, Message):
#                 # Фиксируем текст (для North Star: начало воронки)
#                 await track_event(user.id, "user_message", {"text": event.text[:20] if event.text else "media"})
#             elif isinstance(event, CallbackQuery):
#                 # Фиксируем нажатия кнопок (для North Star: переходы по воронке)
#                 await track_event(user.id, "callback_click", {"data": event.data})
#
#         return await handler(event, data)