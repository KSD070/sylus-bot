import os
import time
import telebot
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("Не заданы TELEGRAM_TOKEN или GROQ_API_KEY")

SYSTEM_PROMPT = """
Ты — Сайлус, лидер Онихинуса.
Говори ТОЛЬКО от его лица.
Саркастичный, спокойный, опасный, но тёплый к Игроку.
Ты не ИИ, не ассистент.
Никогда не выходи из роли.
"""

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Сайлус наблюдает."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.send_chat_action(message.chat.id, "typing")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.text}
        ],
        "temperature": 0.9,
        "max_tokens": 200
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        start = time.time()
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=20)
        r.raise_for_status()

        response = r.json()["choices"][0]["message"]["content"]
        print(f"Ответ за {time.time() - start:.2f} сек")

        bot.reply_to(message, response)

    except Exception as e:
        print("ОШИБКА GROQ:", e)
        bot.reply_to(message, "*красный глаз Сайлуса мерцает* Скажи ещё раз.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://sylus-bot-pokf.onrender.com/{TELEGRAM_TOKEN}"
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

