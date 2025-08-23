import os
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Загрузим переменные окружения из .env (локально)
load_dotenv()

# Подключение к MongoDB
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["zodiaflow"]
collection = db["daily_horoscopes"]

# Ключ DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DeepSeek_API_KEY")

# Список знаков зодиака
ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

def generate_horoscope(sign):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional astrologer who writes inspiring daily horoscopes."},
            {"role": "user", "content": f"Write a daily horoscope for {sign}, 150-200 words, engaging and spiritual."}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def save_to_mongo(sign, content):
    today = datetime.now().strftime("%Y-%m-%d")
    collection.update_one(
        {"sign": sign, "date": today},
        {"$set": {"content": content}},
        upsert=True
    )

def main():
    for sign in ZODIAC_SIGNS:
        try:
            print(f"🔮 Generating for {sign}...")
            content = generate_horoscope(sign)
            save_to_mongo(sign, content)
            print(f"✅ Saved horoscope for {sign}")
        except Exception as e:
            print(f"❌ Error generating for {sign}: {e}")

if __name__ == "__main__":
    main()
