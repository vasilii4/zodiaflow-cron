import os
import requests
from pymongo import MongoClient
from datetime import datetime

# Получаем ключ DeepSeek из переменных окружения
DEEPSEEK_API_KEY = os.getenv("DeepSeek_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# Список знаков зодиака
ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

# Подключаемся к MongoDB
client = MongoClient(MONGODB_URI)
db = client["zodiaflow"]
collection = db["daily_horoscopes"]

def generate_horoscope(sign):
    """Отправка запроса к DeepSeek API"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"Напиши короткий, вдохновляющий гороскоп на сегодня для знака зодиака {sign}, без указания даты."
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты астролог. Генерируй качественные гороскопы на русском языке."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def store_horoscope(sign, content):
    """Сохраняет гороскоп в базу данных"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    collection.update_one(
        {"sign": sign, "date": today},
        {"$set": {"content": content}},
        upsert=True
    )

def main():
    for sign in ZODIAC_SIGNS:
        try:
            print(f"Generating for {sign}...")
            horoscope = generate_horoscope(sign)
            store_horoscope(sign, horoscope)
            print(f"Saved {sign} ✅")
        except Exception as e:
            print(f"❌ Error generating for {sign}: {e}")

if __name__ == "__main__":
    main()
