import os
import psycopg2
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

def get_db_connection():
    """Устанавливает подключение к базе данных с использованием переменных из .env."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except psycopg2.Error:
        return None

def close_db_connection(connection):
    """Закрывает подключение к базе данных."""
    if connection:
        connection.close()

def get_gemini_api_key():
    """Извлекает и расшифровывает Gemini API ключ из таблицы security."""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        with connection.cursor() as cursor:
            # Извлекаем данные из таблицы security
            cursor.execute("SELECT name, value FROM security")
            results = cursor.fetchall()
            credentials = {row[0]: row[1] for row in results}

            # Проверяем наличие всех необходимых ключей
            required_keys = ['GEMINI_API_KEY', 'ENCRYPTION_KEY']
            missing_keys = [key for key in required_keys if key not in credentials]
            if missing_keys:
                return None

            # Получаем ключ шифрования
            fernet = Fernet(credentials['ENCRYPTION_KEY'].encode())

            # Расшифровываем GEMINI_API_KEY
            try:
                decrypted_api_key = fernet.decrypt(credentials['GEMINI_API_KEY'].encode()).decode()
                return decrypted_api_key
            except Exception:
                return None
    except psycopg2.Error:
        return None
    finally:
        close_db_connection(connection)