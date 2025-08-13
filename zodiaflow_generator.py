import openai
import os
import time
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

TARGET_LANGUAGES = ["ru", "es", "pt", "fr", "de", "it", "ar", "hi", "zh"]

today = datetime.utcnow().strftime("%Y-%m-%d")

def generate_prompt(sign, date):
    return f"""
You are the head astrologer at ZodiaFlow, a global astrology platform.

Your job is to generate an insightful, emotional, and inspiring DAILY horoscope for the zodiac sign: {sign}, for the date: {date}.

📌 Write 4 short paragraphs (around 600–700 words total).
📌 The tone must be warm, a little mystical, uplifting, and intuitive — not cold or mechanical.
📌 Use metaphors, feeling-based language, and offer gentle but clear insight.

Each horoscope should include:
1. Emotional theme of the day.
2. Energy level and mental focus.
3. Key areas of life affected (love, communication, finance).
4. One spiritual lesson or advice to reflect on.
5. A closing sentence that gives empowerment or encouragement.

Do not use astrological jargon. Describe how it feels.
Language: English.
"""

def translate_prompt(text, lang_code):
    return f"""
Translate the following horoscope text into {lang_code}.
Keep the tone, poetic structure, and feeling. Do not translate literally — translate expressively.

Text:
{text}
"""

def main():
    client = MongoClient(MONGO_URI)
    db = client["zodiaflow"]
    collection = db["predictions"]

    for sign in ZODIAC_SIGNS:
        print(f"🔮 Generating: {sign}")
        prompt = generate_prompt(sign, today)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9
            )
            base_text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Error generating for {sign}: {e}")
            continue

        collection.update_one(
            {"sign": sign, "lang": "en", "type": "daily", "date": today},
            {"$set": {
                "sign": sign,
                "lang": "en",
                "type": "daily",
                "date": today,
                "text": base_text
            }},
            upsert=True
        )

        for lang in TARGET_LANGUAGES:
            try:
                tr_prompt = translate_prompt(base_text, lang)
                tr_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": tr_prompt}],
                    temperature=0.7
                )
                translated_text = tr_response.choices[0].message.content.strip()

                collection.update_one(
                    {"sign": sign, "lang": lang, "type": "daily", "date": today},
                    {"$set": {
                        "sign": sign,
                        "lang": lang,
                        "type": "daily",
                        "date": today,
                        "text": translated_text
                    }},
                    upsert=True
                )
                print(f"✅ {sign} → {lang}")
            except Exception as e:
                print(f"❌ Translation error {sign} → {lang}: {e}")
                continue

        time.sleep(2)

if __name__ == "__main__":
    main()
