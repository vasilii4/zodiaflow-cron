import os
import datetime
import openai
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Настройка OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Настройка MongoDB
mongo_uri = os.getenv("MONGODB_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["zodiaflow"]
collection = db["daily_horoscopes"]

# Список знаков зодиака
zodiac_signs = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

# Шаблон запроса к GPT
def generate_horoscope(sign: str, date: str):
    prompt = f"""
    Составь краткий, вдохновляющий и правдоподобный гороскоп для знака {sign.capitalize()} на дату {date}.
    Не используй банальности. Стиль — легкий, но уверенный. Максимум 60 слов. Без вступлений и без заключений.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный астролог, который пишет уникальные гороскопы."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Ошибка при генерации для {sign}: {e}")
        return None

# Основной запуск
def main():
    today = datetime.date.today().isoformat()
    for sign in zodiac_signs:
        print(f"⏳ Генерация гороскопа для: {sign} ({today})")
        horoscope = generate_horoscope(sign, today)

        if horoscope:
            # Сохраняем в MongoDB
            collection.update_one(
                {"sign": sign, "date": today},
                {"$set": {"sign": sign, "date": today, "text": horoscope}},
                upsert=True
            )
            print(f"✅ Успешно сохранён гороскоп для {sign}")
        else:
            print(f"❌ Пропущен {sign} из-за ошибки.")

if __name__ == "__main__":
    main()
