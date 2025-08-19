import openai
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Получение API ключа и строки подключения к БД из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongo_uri)
db = client["zodiaflow"]
collection = db["daily_horoscopes"]

signs = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

today = datetime.utcnow().strftime("%Y-%m-%d")

def generate_horoscope(sign):
    prompt = f"Write a short, original daily horoscope for the zodiac sign {sign.title()} for {today}. No intro or sign name, just the prediction."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating for {sign}: {e}")
        return None

for sign in signs:
    print(f"🔮 Generating for {sign}...")
    horoscope = generate_horoscope(sign)
    if horoscope:
        document = {
            "sign": sign,
            "date": today,
            "horoscope": horoscope
        }
        collection.update_one(
            {"sign": sign, "date": today},
            {"$set": document},
            upsert=True
        )
        print(f"✅ Saved for {sign}")
    else:
        print(f"❌ Skipped {sign}")
