import os
import time
import psycopg2
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def get_connection(retries=5, delay=3):
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            print("Подключение к базе данных установлено")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Попытка {i + 1}/{retries}: не удалось подключиться к базе — {e}")
            time.sleep(delay)
    raise ConnectionError("Не удалось подключиться к базе после нескольких попыток.")

def check_user(user_id : int):
    print("user")
    #TODO реализовать


def create_user(user_id : int):
    print("создан")
    #TODO реализовать
