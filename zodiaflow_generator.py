import os
import openai
from datetime import datetime
from pymongo import MongoClient

# 👉 Настройки DeepSeek
openai.api_key = "sk-c20c23ea404d4bc2b6d4ca83d756b354"  # 🔐 Твой API ключ
openai.api_base = "https://api.deepseek.com/v1"

# 👉 Настройки MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")  # обязательно задать в Render
client = MongoClient(MONGODB_URI)
db = client["zodiaflow"]
collection = db["daily_horoscopes"]

# 👉 Список знаков зодиака
zodiac_signs = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

# 👉 Дата для прогноза (на сегодня)
today = datetime.now().strftime("%Y-%m-%d")

def generate_horoscope(sign):
    try:
        print(f"Generating for {sign}...")

        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты профессиональный астролог. Генерируй креативные и вдохновляющие гороскопы."},
                {"role": "user", "content": f"Сгенерируй гороскоп для знака {sign} на {today}, 3 абзаца."}
            ],
            temperature=0.9
        )

        horoscope = response.choices[0].message["content"]

        # 👉 Сохраняем в MongoDB
        collection.update_one(
            {"sign": sign, "date": today},
            {"$set": {"text": horoscope}},
            upsert=True
        )

        print(f"Saved {sign}")
    except Exception as e:
        print(f"❌ Error generating for {sign}: {e}")

if __name__ == "__main__":
    for sign in zodiac_signs:
        generate_horoscope(sign)
